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

#include "net/gnrc/ipv6.h"
#include "net/gnrc/udp.h"
#include "net/ipv6/addr.h"
#include "net/gnrc/ipv6/nc.h"
#include "kernel_types.h"
#include "thread.h"
#include "board.h"


#define ENABLE_DEBUG    (0)
#include "debug.h"

#ifndef NUM_PACKETS
#define NUM_PACKETS         (1010)
#endif
#ifndef MIN_PACKET_SIZE
#define MIN_PACKET_SIZE     (10)
#endif
#ifndef MAX_PACKET_SIZE
#define MAX_PACKET_SIZE     (1211)
#endif
#ifndef STEP_SIZE
#define STEP_SIZE           (10)
#endif

#define DONT_PRINT_DATA     (0)

#define UDP_PORT                            (6414)

#define SERVER_MSG_QUEUE_SIZE               (8)

#define SC_NETIF_IPV6_DEFAULT_PREFIX_LEN    (64)

static int packet_counter = 0;

static int server_socket = -1;
static char server_stack[THREAD_STACKSIZE_DEFAULT];
static msg_t server_msg_queue[SERVER_MSG_QUEUE_SIZE];

static gnrc_netreg_entry_t server = {NULL, GNRC_NETREG_DEMUX_CTX_ALL,
                                   KERNEL_PID_UNDEF};


void led_pulse(void) {
    LED_RED_ON;
    LED_GREEN_ON;
    LED_ORANGE_ON;

    xtimer_usleep(250000);

    LED_RED_OFF;
    LED_GREEN_OFF;
    LED_ORANGE_OFF;
}

static void *_server_thread(void *args)
{
    (void)args;
    msg_t msg;
    msg_init_queue(server_msg_queue, SERVER_MSG_QUEUE_SIZE);

    /* start server (which means registering pktdump for the chosen port) */
    server.pid = thread_getpid();
    server.demux_ctx = (uint32_t)UDP_PORT;
    gnrc_netreg_register(GNRC_NETTYPE_UDP, &server);
    server_socket = 0;
    DEBUG("Success: started UDP server on port %" PRIu16 "\n", UDP_PORT);

     while (1) {
        msg_receive(&msg);

        switch (msg.type) {
            case GNRC_NETAPI_MSG_TYPE_RCV:

                packet_counter++;
                if (packet_counter == NUM_PACKETS) {
                    led_pulse();
                    packet_counter = 0;
                }

                gnrc_pktbuf_release((gnrc_pktsnip_t *)msg.content.ptr);
                break;
            default:
                DEBUG("PKTDUMP: received something unexpected");
                break;
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

static char data[MAX_PACKET_SIZE];
int main(void)
{
    LED_RED_OFF;
    LED_GREEN_OFF;
    LED_ORANGE_OFF;
    udp_start_server();

    for (int i = 0; i < MAX_PACKET_SIZE; i++) {
        data[i] = i;
    }

    uint8_t port[2];
    port[0] = (uint8_t)UDP_PORT;
    port[1] = (uint8_t)(UDP_PORT >> 8);

    gnrc_pktsnip_t *payload, *udp, *ip;
    gnrc_netreg_entry_t *sendto;

#if !LOOPBACK_MODE

    kernel_pid_t ifs[GNRC_NETIF_NUMOF];
    ipv6_addr_t src_addr, dest_addr;
    gnrc_ipv6_nc_t *nc_entry = NULL;

    /* set global unicast SOURCE  address */
    //char addr_str[] = "fe80::3432:4833:46d9:8a13";
    char addr_str[]= "2001:cafe:0000:0002:0222:64af:126b:8a14";

    gnrc_netif_get(ifs);

    /* reset address on interface */
    gnrc_ipv6_netif_reset_addr(ifs[0]);

    if (ipv6_addr_from_str(&src_addr, addr_str) == NULL) {
        DEBUG("error: unable to parse IPv6 address.");
        return 1;
    }
    if (gnrc_ipv6_netif_add_addr(ifs[0], &src_addr, SC_NETIF_IPV6_DEFAULT_PREFIX_LEN, false) == NULL) {
        DEBUG("Error: unable to add IPv6 address");
    }

    /* set global unicast DESTINATION  address */
    char dst_addr_str[] = "2001:cafe:0000:0002:0222:64af:126b:8a15";
    //char dst_addr_str[] = "fe80::3432:4833:46d9:8a13";

    /* set hhardware address of receiver */
    //uint8_t hwaddr[2] = {0x8a, 0x14};
    uint8_t hwaddr[8] = {0xce, 0x3d, 0xe8, 0x5a, 0x0a, 0x4d, 0x7b, 0xd8};
    //int8_t hwaddr[8] = {0x5a, 0x5a, 0x50, 0x6b, 0x51, 0x7e, 0x00, 0xd2};


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

#if ENABLE_DEBUG
    _ipv6_nc_list();
#endif

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

    for(unsigned int j = MIN_PACKET_SIZE; j < MAX_PACKET_SIZE; j+=STEP_SIZE) {
    
        for (unsigned int i = 0; i < NUM_PACKETS; i++) {

            payload = gnrc_pktbuf_add(NULL, &data[0], j, GNRC_NETTYPE_UNDEF);

            udp = gnrc_udp_hdr_build(payload, port, sizeof(port), port, sizeof(port));

            ip = gnrc_ipv6_hdr_build(udp, NULL, 0, (uint8_t *)&dest_addr, sizeof(dest_addr));

            sendto = gnrc_netreg_lookup(GNRC_NETTYPE_UDP, GNRC_NETREG_DEMUX_CTX_ALL);

            gnrc_pktbuf_hold(ip, gnrc_netreg_num(GNRC_NETTYPE_UDP,
                                         GNRC_NETREG_DEMUX_CTX_ALL) - 1);

            gnrc_netapi_send(sendto->pid, ip);

        }
    }
    puts("DONE");
    return 0;
}