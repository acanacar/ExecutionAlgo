import concurrent.futures
import time

start = time.perf_counter()


def do_something(seconds):
    print('Sleeping {} second(s)...'.format(seconds))
    time.sleep(seconds)
    return 'Done Sleeping...{}'.format(seconds)


with concurrent.futures.ProcessPoolExecutor() as executor:
    secs = [5, 4, 3, 2, 1]
    results = executor.map(do_something, secs)

    # for result in results:
    #     print(result)

finish = time.perf_counter()

print('Finished in {} second(s)'.format(round(finish-start, 2)))