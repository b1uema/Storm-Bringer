# 测试 dynomite 异地多活的一致性。
import redis
import time
import threading


TEST_KEY = "test"
REDIS_LOCAL_CONF = {
        "host": "localhost",
        "port": 8102
    }
REDIS_LOCAL_CONF2 = {
        "host": "localhost",
        "port": 6379
}
REDIS_REMOTE_CONF = {
        "host": "140.143.46.111",
        "port": 6379
    }
THREAD_TIMES = 100
INCR_TIMES = 20000


def link_redis(conf):
    # 链接数据库，conf字典类型
    client = redis.Redis(host=conf["host"], port=conf["port"], decode_responses=True)
    return client


def redis_incr(redis_conf, times):
    # 数据库操作
    client = link_redis(redis_conf)
    for i in range(times):
        try:
            client.incr(TEST_KEY)
        except Exception as e:
            #time.sleep(0.5)
            print(e)


if __name__ == "__main__":
    thread_list = []
    for i in range(THREAD_TIMES):
        t = threading.Thread(target=redis_incr, args=(REDIS_LOCAL_CONF, INCR_TIMES))
        thread_list.append(t)

    c_local = link_redis(REDIS_LOCAL_CONF)
    c_local.set(TEST_KEY, 0)
    c_remote = link_redis(REDIS_REMOTE_CONF)

    for t in thread_list:
        t.setDaemon(True)
        t.start()
        t.join()

    print("local:"+link_redis(REDIS_LOCAL_CONF2).get(TEST_KEY))
    time.sleep(2)
    print("remote:"+c_remote.get(TEST_KEY))
