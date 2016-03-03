/*
 * Copyright (C) 2015 HAW Hamburg
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     examples
 * @{
 *
 * @file
 * @brief
 *
 * @author      Peter Kietzmann <peter.kietzmann@haw-hamburg.de>
 *
 * @}
 */

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <unistd.h>

#include "net/gnrc/ipv6.h"
#include "net/gnrc/udp.h"
#include "net/ipv6/addr.h"

#include "net/af.h"
#include "net/conn/ip.h"
#include "net/conn/udp.h"

#include "kernel_types.h"

#include "thread.h"

#define ENABLE_DEBUG    (0)
#include "debug.h"

#ifndef PACKET_SIZE
#define PACKET_SIZE     (100)
#endif

#define UDP_PORT                (9)

#define SERVER_MSG_QUEUE_SIZE   (8)

#define SC_NETIF_IPV6_DEFAULT_PREFIX_LEN (64)

/* Server */
static conn_udp_t server_conn;


static int server_socket = -1;
static char server_buffer[PACKET_SIZE];
static char server_stack[THREAD_STACKSIZE_DEFAULT];
static msg_t server_msg_queue[SERVER_MSG_QUEUE_SIZE];

static void *_server_thread(void *args)
{
    (void)args;

    msg_init_queue(server_msg_queue, SERVER_MSG_QUEUE_SIZE);
    ipv6_addr_t server_addr = IPV6_ADDR_UNSPECIFIED;

    if (conn_udp_create(&server_conn, &server_addr, sizeof(server_addr), AF_INET6,
                    UDP_PORT) < 0){ // byteorder??????
        DEBUG("error initializing socket");
        return NULL;
    }
    server_socket = 0;
    DEBUG("Success: started UDP server on protocol %"PRIu8" and port %" PRIu16 "\n", AF_INET6, UDP_PORT);

    while (1) {
        int res;
        ipv6_addr_t src;
        size_t src_len = sizeof(ipv6_addr_t);

        if ((res = conn_udp_recvfrom(&server_conn, server_buffer, sizeof(server_buffer), &src,
                                    &src_len, NULL)) < 0) { // oder hier senderport noch rausziehen
            DEBUG("Error on receive");
        }
        else if (res == 0) {
            DEBUG("Peer did shut down");
        }
        else {
            DEBUG("Received data of size: %i\n", res);
        }
    }
    return NULL;
}

static int udp_start_server(void)
{

    int port = UDP_PORT;

    /* check if server is already running */
    if (server_socket >= 0) {
        DEBUG("Error: server already running");
        return 1;
    }
    /* start server (which means registering pktdump for the chosen port) */
    if (thread_create(server_stack, sizeof(server_stack), THREAD_PRIORITY_MAIN - 1,
                      CREATE_STACKTEST, _server_thread, &port, "UDP server") <= KERNEL_PID_UNDEF) {
        server_socket = -1;
        DEBUG("error initializing thread");
        return 1;
    }
    return 0;
}

static char data[PACKET_SIZE];
int main(void)
{
    udp_start_server();

    for (int i = 0; i < PACKET_SIZE; i++) {
        data[i] = i;
    }
#if !LOOPBACK_MODE

    ipv6_addr_t addr;
    kernel_pid_t ifs[GNRC_NETIF_NUMOF];

    /* set global unicast SOURCE  address */
    char addr_str[]= "2001:cafe:0000:0002:0222:64af:126b:8a14";

    gnrc_netif_get(ifs);

    /* reset address on interface */
    gnrc_ipv6_netif_reset_addr(ifs[0]);

    if (ipv6_addr_from_str(&addr, addr_str) == NULL) {
        DEBUG("error: unable to parse IPv6 address.");
        return 1;
    }
    if (gnrc_ipv6_netif_add_addr(ifs[0], &addr, SC_NETIF_IPV6_DEFAULT_PREFIX_LEN, false) == NULL) {
        DEBUG("Error: unable to add IPv6 address");
    }

    ipv6_addr_t dest_addr;
    gnrc_ipv6_nc_t *nc_entry = NULL;
    /* set global unicast DESTINATION  address */
    char dst_addr_str[] = "2001:cafe:0000:0002:0222:64af:126b:8a14";

    /* set hhardware address of receiver */
    uint8_t hwaddr[8] = {0x10, 0x22, 0x64, 0xaf, 0x12, 0x6b, 0x8a, 0x14};

    if (ipv6_addr_from_str(&dest_addr, dst_addr_str) == NULL) {
        DEBUG("error: unable to parse IPv6 address.");
        return 1;
    }

    if ((nc_entry = gnrc_ipv6_nc_add(ifs[0], &dest_addr, hwaddr, sizeof(hwaddr), 0)) == NULL) {
        DEBUG("error: unable to add address to neighbor cache.");
        return 1;
    }
    else{
        nc_entry->flags &= ~(GNRC_IPV6_NC_STATE_MASK);
        nc_entry->flags |= (GNRC_IPV6_NC_STATE_REACHABLE);
        nc_entry->flags &= ~(GNRC_IPV6_NC_TYPE_MASK);
        nc_entry->flags |= (GNRC_IPV6_NC_TYPE_REGISTERED); /* this is the important thing */
        DEBUG("added address to NC\n");
    }
#else /* LOOPBACK_MODE */

    DEBUG("This is IPV6 loopback mode\n");
    char dst_addr_str[] = "::1";
    ipv6_addr_t dest_addr;

    if (ipv6_addr_from_str(&dest_addr, dst_addr_str) == NULL) {
        DEBUG("error: unable to parse IPv6 address.");
        return 1;
    }


#endif
/*
    // Disable retrans of transceiver, just for debug
    uint8_t num_retrans = 0;
    gnrc_netapi_set(ifs[0], NETOPT_RETRANS, 0, &num_retrans,
                            sizeof(num_retrans));
*/

    conn_udp_sendto(&data, PACKET_SIZE, NULL, 0,(struct sockaddr *)&dest_addr, sizeof(dest_addr), 
        AF_INET6, UDP_PORT, UDP_PORT);
    
    puts("end");

    return 0;
}