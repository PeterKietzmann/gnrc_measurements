Here is some code that I used for testing. You'll need some dependencies:

A link layer reflector driver that shorts the link. Note that you need to have the same *scr* and *dst* address when doing such kind of loopback. To avoid running into the IPv6 loopback, there is a small workaround in that branch which takes out some loopback checks if `LOOPBACK_MODE` is not defined 
[l2_reflector branch](https://github.com/PeterKietzmann/RIOT/tree/add_l2_reflector_driver)

Attention! Using the above application might cause hard faults on a board. In that case you might want to apply the following patch on your master to increase the stack size of the main thread
[patch file](https://github.com/PeterKietzmann/gnrc_measurements/blob/master/0001-increased-main-stacksize-for-test-app.patch)