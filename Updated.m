% Clear workspace
clear;
clc;

%% Parameters
lw = 2; 
fs = 20; 
FS = 28;

% Figures: always docked
set(0,'DefaultFigureWindowStyle','docked') 

% Figures: background 
set(0,'DefaultFigureColor','white')

% Axes: font size
set(0,'DefaultAxesFontSize',20) 

% Legend: font size
set(0, 'DefaultLegendFontSize', 18, 'DefaultLegendFontSizeMode', 'manual'); 

% Plot: linewidth 
set(0,'DefaultLineLineWidth',2); 

% Axes: grid
set(0, 'DefaultAxesXGrid', 'on');
set(0, 'DefaultAxesYGrid', 'on');
set(0, 'DefaultAxesZGrid', 'on');

% Axes: grid minor
set(0, 'DefaultAxesXMinorGrid', 'on', 'DefaultAxesXMinorGridMode', 'manual');
set(0, 'DefaultAxesYMinorGrid', 'on', 'DefaultAxesYMinorGridMode', 'manual');
set(0, 'DefaultAxesZMinorGrid', 'on', 'DefaultAxesZMinorGridMode', 'manual');

% Tiled layout: padding 
set(0,'DefaultTiledlayoutPadding','compact'); 

%% List all relevant files
list_names = dir('*WaveData*.csv');

%% Process each file
for k = 1:length(list_names)
    filename = list_names(k).name; 
    fprintf('Processing file: %s\n', filename);

    % Open file to find the data start line
    fileID = fopen(filename, 'r');
    line = fgetl(fileID);
    dataStartLine = 0;
    lineCounter = 0;

    % Find the line with "Wavelength(A)"
    while ischar(line)
        lineCounter = lineCounter + 1;
        if contains(line, 'Wavelength(A)')
            dataStartLine = lineCounter + 1; % Data starts from the next line
            break;
        end
        line = fgetl(fileID);
    end
    fclose(fileID);

    if dataStartLine == 0
        error('The header "Wavelength(A)" was not found in file: %s', filename);
    end

    % Read the data starting from the detected line
    opts = delimitedTextImportOptions("NumVariables", 2);
    opts.DataLines = [dataStartLine Inf];
    opts.Delimiter = ",";
    opts.VariableNames = ["Wavelength", "Power"];
    opts.VariableTypes = ["double", "double"];
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";

    data = readtable(filename, opts);
    WL = data.Wavelength;
    P = 10 .* log10(abs(data.Power));

    %% Noise estimation
    rbw = 1.5; % Assumed resolution bandwidth multiplier
    [~, npow] = snr(abs(data.Power), WL - WL(1), rbw, "power");
    noise = median(P(P < npow)); % Median of values below noise threshold

    %% Peak detection
minDistance = 1.25; % Minimum distance between peaks (nm)
minHeight = noise + 2.5; % Minimum peak height (dB)
[peaks, locations] = findpeaks(P, WL, 'MinPeakDistance', minDistance, 'MinPeakHeight', minHeight);

%% Signal-to-noise ratio (SNR)
numPeaks = length(peaks);
if numPeaks > 0
    SNR = peaks - noise; % SNR in dB
else
    SNR = [];
end

%% Filter peaks by SNR > 8
validPeaks = SNR > 8; % Find peaks with SNR greater than 8
validPeaksLocations = locations(validPeaks); % Get locations of valid peaks
validPeaksValues = peaks(validPeaks); % Get values of valid peaks
validSNR = SNR(validPeaks); % Get SNR values for valid peaks

%% Plot results
figure;
t = tiledlayout(1, 1, 'TileSpacing', 'tight');
ax1 = nexttile(1);

plot(ax1, WL, P, 'LineWidth', lw);
hold on;

% Define an offset for the noise line text to position it slightly above the line
noiseTextOffset = 4;  % Adjust this value to control how much above the line the text appears

% Plot the noise line at the original position
yline(ax1, noise, 'k--', 'LineWidth', lw);

% Use the text function to manually position the noise label slightly above the line
text(ax1, min(WL), noise + noiseTextOffset, ['Noise ~ ' num2str(round(noise, 1)) ' dBm'], ...
    'FontSize', fs, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');

if numel(validPeaksLocations) > 0
    % Annotate only valid peaks (SNR > 8)
    arrayfun(@(i) text(ax1, validPeaksLocations(i) + 0.1, validPeaksValues(i), ...
        [num2str(round(validPeaksValues(i), 1)) ' dBm' newline num2str(round(validSNR(i), 1)) ' dB SNR'], ...
        'FontSize', FS, 'VerticalAlignment', 'bottom', 'Interpreter', 'none'), 1:numel(validPeaksLocations));
else
    % Move the "No valid peaks" text slightly above the noise line
    text(ax1, mean(WL), noise + noiseTextOffset, 'No valid peaks (SNR > 8)', ...
         'FontSize', FS, 'HorizontalAlignment', 'center');
end

ylim(ax1, [-88, 10]);
xlabel(t, 'Wavelength (nm)', 'FontSize', FS);
ylabel(t, 'Optical Power (dBm)', 'FontSize', FS);
title(ax1, sprintf('Optical Spectrum: %s', filename), 'FontSize', FS, 'Interpreter', 'none');

% Save figures
saveas(gcf, ['Figures\' sprintf('%03d', k) '_' filename(1:end-4)], 'fig');
saveas(gcf, ['Figures\' sprintf('%03d', k) '_' filename(1:end-4)], 'png');

end