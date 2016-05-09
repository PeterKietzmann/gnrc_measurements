import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend_handler import HandlerLine2D


NUM_POINTS = 121;
X_PLOT_VEC = np.arange(10, 1211, 10)

lower_quantil = 5;
upper_quantil= 100-lower_quantil;


# LINUX stack ipv6 loopback

posix_udp_ip_linux = np.loadtxt("single_measure_temp.txt")
posix_udp_ip_linux = posix_udp_ip_linux / 1000; #ns to us


posix_udp_ip_linux_mean = np.mean(posix_udp_ip_linux, axis=1);
posix_udp_ip_linux_std=np.std(posix_udp_ip_linux, axis=1);

posix_udp_ip_linux_lower_quantil = np.percentile(posix_udp_ip_linux, lower_quantil, axis=1);
posix_udp_ip_linux_lower_quantil = posix_udp_ip_linux_mean - posix_udp_ip_linux_lower_quantil;

posix_udp_ip_linux_upper_quantil = np.percentile(posix_udp_ip_linux, upper_quantil, axis=1);
posix_udp_ip_linux_upper_quantil = posix_udp_ip_linux_upper_quantil - posix_udp_ip_linux_mean;

plt.figure()
asymm_error=[posix_udp_ip_linux_lower_quantil, posix_udp_ip_linux_upper_quantil];
plt.errorbar(X_PLOT_VEC, posix_udp_ip_linux_mean, yerr=asymm_error)
plt.title('Mean and 5% quantile bars')

plt.ylabel('Linux Processing Time [$\mu$s]')
plt.xlabel('UDP Payload [Byte]')
plt.xlim([0, 1200])
plt.show()

plt.figure()
plt.errorbar(X_PLOT_VEC, posix_udp_ip_linux_mean, yerr=posix_udp_ip_linux_std)
plt.show()

plt.figure()
plt.plot(X_PLOT_VEC, posix_udp_ip_linux)
plt.show()

legend_vec = [ 'RIOT iotlab-m3', 'RIOT native Linux' ,'Linux'];

fmt_vec=['-k', ':k', '--k'];

linewidth_vec = [2, 2, 2 ];

fontsize_labels = 32;
fontsize_ticks = 30;
fontsize_text = 32;
fontsize_legend = 32;


fig = plt.figure(figsize=(22,10))
ax = fig.add_subplot(111)


asymm_error=[posix_udp_ip_iotlab_m3_lower_quantil, posix_udp_ip_iotlab_m3_upper_quantil];
ax.errorbar(X_PLOT_VEC, posix_udp_ip_iotlab_m3_mean, yerr=asymm_error, fmt=fmt_vec[0], label=legend_vec[0], linewidth=linewidth_vec[0])

ax2 = ax.twinx()
asymm_error=[posix_udp_ip_native_lower_quantil, posix_udp_ip_native_upper_quantil];
ax2.errorbar(X_PLOT_VEC, posix_udp_ip_native_mean, yerr=asymm_error, fmt=fmt_vec[1], label=legend_vec[1], linewidth=linewidth_vec[1])
### test with std deviation
#ax2.errorbar(X_PLOT_VEC, posix_udp_ip_native_mean, yerr=posix_udp_ip_native_std, fmt=fmt_vec[1], label=legend_vec[1], linewidth=linewidth_vec[1])



ax.set_ylabel('RIOT Processing Time [$\mu$s]', fontsize=fontsize_labels)
ax2.set_ylabel('Linux Processing Time [$\mu$s]', fontsize=fontsize_labels)

## genreal settings
ax.set_xlim([0, 1200])
ax.set_ylim([0, 1100])
#ax2.set_ylim([11.8, 15.2])
#ax2.set_ylim([10, 30])

ax.tick_params(labelsize=fontsize_ticks,  length=10,  which='major', pad=12)
ax2.tick_params(axis='y', labelsize=fontsize_ticks,  length=10,  which='major', pad=12)

ax2.yaxis.labelpad = 20

ax.set_xlabel('Protocol Payload [Bytes]', fontsize=fontsize_labels)
#plt.ylabel('Processing Time [$\mu$s]', fontsize=fontsize_labels)

ax.legend(loc='upper left', fontsize=fontsize_legend)
ax2.legend(loc='lower right', fontsize=fontsize_legend)


# export figure
plt.savefig("compare_time_board_pc.pdf",bbox_inches='tight');
plt.show()
