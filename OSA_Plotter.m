% close all
clear 
clc

%% 
lw              = 2; 
fs              = 20; 
FS              = 28;
ms              = 8; 
MS              = 10;

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

%% 
list_names      = dir('*WaveData*.csv'); 
%%
T = 35;             % [°C]

%% 
for k = 3:3 %length(list_names)

    filename    = list_names(k).name; 
    SOA_id      = 'TS7024'; 
    data        = readmatrix(filename); 

    WL = data(:,1); 
    P  = (10.*log10(abs(data(:,2)))); 
    
   %% Set up the Import Options and import the data
    opts = delimitedTextImportOptions("NumVariables", 3);
    
    % Specify range and delimiter
    opts.DataLines = [1, 115];
    opts.Delimiter = ",";
    
    % Specify column names and types
    opts.VariableNames = ["WavelengthA", "LevelA", "VarName3"];
    opts.VariableTypes = ["string", "double", "string"];
    
    % Specify file level properties
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";
    
    % Specify variable properties
    opts = setvaropts(opts, ["WavelengthA", "VarName3"], "WhitespaceRule", "preserve");
    opts = setvaropts(opts, ["WavelengthA", "VarName3"], "EmptyFieldRule", "auto");
    
    % Import the data
    dataHeader = readtable(filename, opts);
   
    % Clear temporary variables
    clear opts 

    %% 
    rbw_nm      = dataHeader{11,2}; % Resolution [nm] 
    rbw_nm_act  = dataHeader{12,2}; % Actual resolution [nm]
    
    lambda0     = dataHeader{ 5,2};  % Central wavelength [nm] 

    %% 
    c = 299792458;                  % Speed of light in vacuum (m/s) 
        
    %% 
    % figure 
    rbw = rbw_nm*1.5; 
    
    % snr(abs(data(:,2)),WL-WL(1),rbw,"power")

    [~,npow] = snr(abs(data(:,2)),WL-WL(1),rbw,"power"); 
    noise = median(P(P<npow)); 
 
    %%
    figure 
    t = tiledlayout(1,1,'TileSpacing', 'tight'); 
    ax1 = nexttile(1); 

    plot(ax1,WL,P)
    hold on 
    yline(ax1,noise,'k--',['Noise ~ ' num2str(round(noise,1)) ' dBm'],'LineWidth',lw,'FontSize',fs,'LabelHorizontalAlignment','left','LabelVerticalAlignment','top');
    
    ylim(ax1, [-88 10])

    xlabel(t,'Wavelength (nm)','FontSize',fs)
    ylabel(t,'Optical Power (dBm)','FontSize',fs) 
    
    title (ax1,'Optical Spectrum','FontSize',FS)
   
    ax1.FontSize = fs;
    
    %% 
    % Parameters
    minDistance = 1.25; % Minimum distance between peaks (nm)
    minHeight   = noise + 2.5; % Minimum height of peaks (dB) 
    minWidth    = rbw_nm*1; 
    minProminence = 22; 

    % [pks,locs] = findpeaks(P,WL,'NPeaks',1,'SortStr','descend','MinPeakDistance', minDistance);
    % [peaks,locations,width] = findpeaks(P,WL,'SortStr','descend','MinPeakDistance', minDistance,'MinPeakHeight',minHeight,'MinPeakWidth',minWidth);
    [peaks,locations,width,prominence] = findpeaks(P,WL,'SortStr','descend','MinPeakDistance', minDistance,'MinPeakHeight',minHeight);
 
    % Analyze number of peaks
    numPeaks = length(peaks);
    
    % Display results
    % fprintf('Number of peaks found: %d\n', numPeaks);
    if numPeaks > 1
        [pks,locs] = findpeaks(P,WL,'NPeaks',2,'SortStr','descend','MinPeakDistance', minDistance);
        signal = pks;
        SNR = signal - noise; % SNR in dB 
        % Annotate each peak without a for loop
        arrayfun(@(i) text(ax1,locs(i)+0.1,pks(i),[num2str(round(pks(i),1)) ' dBm ' newline num2str(round(SNR(i),1)) ' dB SNR'],'FontSize',FS), 1:length(pks));

     
    elseif numPeaks > 0
        [pks,locs] = findpeaks(P,WL,'NPeaks',1,'SortStr','descend','MinPeakDistance', minDistance);
        signal = pks;
        SNR = signal - noise; % SNR in dB 
        % Annotate each peak without a for loop
        arrayfun(@(i) text(ax1,locs(i)+0.1,pks(i),[num2str(round(pks(i),1)) ' dBm ' newline num2str(round(SNR(i),1)) ' dB SNR'],'FontSize',FS), 1:length(pks));    
    else
        % disp('No peaks found.');
        signal = noise;
    end


         
    %% Save the figure
    
    % saveas (gcf,['Figures\' sprintf('%03d', k) '_' filename(1:end-4)],'fig')
    % saveas (gcf,['Figures\' sprintf('%03d', k) '_' filename(1:end-4)],'png')    

end 

%% 
for k = 1:2

    filename    = list_names(k).name; 
    SOA_id      = 'TS7024'; 
    data        = readmatrix(filename); 

    WL = data(:,1); 
    P  = (10.*log10(abs(data(:,2)))); 
    
    % Set up the Import Options and import the data
    opts = delimitedTextImportOptions("NumVariables", 3);
    
    % Specify range and delimiter
    opts.DataLines = [1, 115];
    opts.Delimiter = ",";
    
    % Specify column names and types
    opts.VariableNames = ["WavelengthA", "LevelA", "VarName3"];
    opts.VariableTypes = ["string", "double", "string"];
    
    % Specify file level properties
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";
    
    % Specify variable properties
    opts = setvaropts(opts, ["WavelengthA", "VarName3"], "WhitespaceRule", "preserve");
    opts = setvaropts(opts, ["WavelengthA", "VarName3"], "EmptyFieldRule", "auto");
    
    % Import the data
    dataHeader = readtable(filename, opts);
   
    % Clear temporary variables
    clear opts 

    % 
    rbw_nm      = dataHeader{11,2}; % Resolution [nm] 
    rbw_nm_act  = dataHeader{12,2}; % Actual resolution [nm]
    
    lambda0     = dataHeader{ 5,2};  % Central wavelength [nm] 
    
    wl_start    = dataHeader{7,2};  % Start wavelength [nm] 
    wl_end      = dataHeader{8,2};  % End wavelength [nm] 

    %
    figure 
    t = tiledlayout(1,1,'TileSpacing', 'tight'); 
    ax1 = nexttile(1); 

    plot(ax1,WL,P)
   
    xlim(ax1,[wl_start wl_end])
    ylim(ax1, [-88 10])

    xlabel(t,'Wavelength (nm)','FontSize',FS)
    ylabel(t,'Optical Power (dBm)','FontSize',FS) 
    
    title (ax1,'Optical Spectrum','FontSize',FS)
   
    ax1.FontSize = fs;
             
    % Save the figure
    
    saveas (gcf,['Figures\' sprintf('%03d', k) '_' filename(1:end-4)],'fig')
    saveas (gcf,['Figures\' sprintf('%03d', k) '_' filename(1:end-4)],'png')    

end 
