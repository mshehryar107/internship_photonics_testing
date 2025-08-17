#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#%%
Gain_Curr = [120, 150, 180]
V_CW  = [1.398, 1.341, 1.322]
V_QCW = [1.420, 1.399, 1.334]

fig, ax = plt.subplots()
twin1 = ax.twinx()
p1, = ax.plot(Gain_Curr, V_QCW , "-bo", label="PD Voltage QCW")
p2, = twin1.plot(Gain_Curr, V_CW , "-ro", label="PD Voltage QCW")
#ax.set_xlim(104, 126)
#ax.set_ylim(0.5, 1.5)
#twin1.set_ylim(0.5, 1.5)

ax.set_title('OL_SOA_TS7024_CW_QCW', fontsize=15) 
ax.set_xlabel("Gain Current (mA)", fontsize=14)
ax.set_ylabel("PD Voltage QCW (V)", fontsize=14)
twin1.set_ylabel("PD Voltage QCW (V)", fontsize=14)
ax.yaxis.label.set_color(p1.get_color())
twin1.yaxis.label.set_color(p2.get_color())
tkw = dict(size=4, width=1.5)
ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
ax.tick_params(axis='x', **tkw)
ax.minorticks_on()
twin1.minorticks_on()
twin1.yaxis.grid(color = 'grey', which='major', linestyle = '-', linewidth = 0.5)
ax.xaxis.grid(color = 'grey', which='major', linestyle = '-', linewidth = 0.5)
twin1.yaxis.grid(color = 'grey', which='minor', linestyle = '--', linewidth = 0.4)
ax.xaxis.grid(color = 'grey', which='minor', linestyle = '--', linewidth = 0.4)
#ax.legend(handles=[p1,p2], bbox_to_anchor=(0.45,0.95))
#plt.savefig('OL_'+str(Device)+'_'+str(Set_temp)+'C_Power_'+str(diode)+'_1.png',dpi=300)
plt.show()