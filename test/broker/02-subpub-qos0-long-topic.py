#!/usr/bin/env python3

# Test whether a client subscribed to a topic receives its own message sent to that topic, for long topics.

from mosq_test_helper import *

def do_test(start_broker, topic, succeeds):
    rc = 1
    mid = 53
    keepalive = 60
    connect_packet = mosq_test.gen_connect("02-subpub-qos0-long-topic", keepalive=keepalive)
    connack_packet = mosq_test.gen_connack(rc=0)

    subscribe_packet = mosq_test.gen_subscribe(mid, topic, 0)
    suback_packet = mosq_test.gen_suback(mid, 0)

    publish_packet = mosq_test.gen_publish(topic, qos=0, payload="message")

    port = mosq_test.get_port()
    if start_broker:
        broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port)

    try:
        sock = mosq_test.do_client_connect(connect_packet, connack_packet, timeout=20, port=port)

        if succeeds == True:
            mosq_test.do_send_receive(sock, subscribe_packet, suback_packet, "suback")
            mosq_test.do_send_receive(sock, publish_packet, publish_packet, "publish")
        else:
            mosq_test.do_send_receive(sock, subscribe_packet, b"", "suback")

        rc = 0

        sock.close()
    except mosq_test.TestError:
        pass
    finally:
        if start_broker:
            broker.terminate()
            broker.wait()
            (stdo, stde) = broker.communicate()
            if rc:
                print(stde.decode('utf-8'))
                exit(rc)
        else:
            return rc


def all_tests(start_broker=False):
    rc = do_test(start_broker, "/"*200, True) # 200 max hierarchy limit
    if rc:
        return rc;
    rc = do_test(start_broker, "abc/"*199+"d", True) # 200 max hierarchy limit, longer overall string than 200
    if rc:
        return rc;

    rc = do_test(start_broker, "/"*201, False) # Exceeds 200 max hierarchy limit
    if rc:
        return rc;
    rc = do_test(start_broker, "abc/"*201+"d", False) # Exceeds 200 max hierarchy limit, longer overall string than 200
    if rc:
        return rc;
    return 0

if __name__ == '__main__':
    all_tests(True)