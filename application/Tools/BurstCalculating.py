import datetime
import math

import numpy as np


def StringToDate(s):
    year = s[0:4]
    month = s[4:6]
    day = s[6:]
    date = datetime.date(int(year), int(month), int(day))
    return date


def OffsetToGap(offset):
    offsetTrans = []
    for i in offset:
        offsetTrans.append(StringToDate(str(i)))

    gap = np.diff(offsetTrans)
    gapInt = []
    for j in gap:
        # print(int(j.total_seconds() / 60 / 60 / 24))
        gapInt.append(int(j.total_seconds() / 60 / 60 / 24))
    return gapInt


def kleinberg(offsets, s=2, gamma=1.0):
    if s <= 1:
        raise ValueError("s must be greater than 1!")
    if gamma <= 0:
        raise ValueError("gamma must be positive!")
    if len(offsets) < 1:
        raise ValueError("offsets must be non-empty!")

    offsets = np.array(offsets, dtype=object)

    if offsets.size == 1:
        bursts = np.array([0, offsets[0], offsets[0]], ndmin=2, dtype=object)
        return bursts

    offsets = np.sort(offsets)
    print("Ket qua sort")
    print(offsets)
    # Edit here to change the FORMAT from number to DATE
    gaps = OffsetToGap(offsets)
    print('gaps=', gaps)
    if not np.all(gaps):
        raise ValueError("Input cannot contain events with zero time between!")

    T = np.sum(gaps)
    n = np.size(gaps)
    g_hat = T / n

    k = int(math.ceil(float(1 + math.log(T, s) + math.log(1 / np.amin(gaps), s))))
    print('k=', k)
    gamma_log_n = gamma * math.log(n)

    def tau(i, j):
        if i >= j:
            return 0
        else:
            return (j - i) * gamma_log_n

    alpha_function = np.vectorize(lambda x: s ** x / g_hat)
    alpha = alpha_function(np.arange(k))

    def f(j, x):
        return alpha[j] * math.exp(-alpha[j] * x)

    C = np.repeat(float("inf"), k)
    C[0] = 0
    print('C=', C)
    q = np.empty((k, 0))
    print('q=', q)
    for t in range(n):
        C_prime = np.repeat(float("inf"), k)
        q_prime = np.empty((k, t + 1))
        q_prime.fill(np.nan)

        for j in range(k):
            cost_function = np.vectorize(lambda x: C[x] + tau(x, j))
            cost = cost_function(np.arange(0, k))

            el = np.argmin(cost)

            if f(j, gaps[t]) > 0:
                C_prime[j] = cost[el] - math.log(f(j, gaps[t]))

            if t > 0:
                q_prime[j, :t] = q[el, :]

            q_prime[j, t] = j + 1

        C = C_prime
        q = q_prime

    j = np.argmin(C)
    q = q[j, :]
    print('q=', q)
    prev_q = 0

    N = 0
    for t in range(n):
        if q[t] > prev_q:
            N = N + q[t] - prev_q
        prev_q = q[t]

    bursts = np.array([np.repeat(np.nan, N), np.repeat(offsets[0], N), np.repeat(offsets[0], N)], ndmin=2,
                      dtype=object).transpose()
    print('bursts', bursts)
    burst_counter = -1
    prev_q = 0
    stack = np.repeat(np.nan, N)
    stack_counter = -1
    # print('stack=', stack)
    # print('stack_counter =', stack_counter)
    # print('n=', n)
    for t in range(n):
        if q[t] > prev_q:
            num_levels_opened = q[t] - prev_q
            for i in range(int(num_levels_opened)):
                burst_counter += 1
                bursts[burst_counter, 0] = prev_q + i
                bursts[burst_counter, 1] = offsets[t]
                stack_counter += 1
                stack[stack_counter] = burst_counter
        elif q[t] < prev_q:
            num_levels_closed = prev_q - q[t]
            # print('num_levels_closed =', num_levels_closed)
            for i in range(int(num_levels_closed)):
                # print('stack_counter in rang i=', stack_counter, ',', int(stack[stack_counter]))
                bursts[int(stack[stack_counter]), 2] = offsets[t]
                stack_counter -= 1
        prev_q = q[t]
        # print('t=', t)
        # print('stack_counter=', stack_counter)
    # print('stack_counter_outer=', stack_counter)
    while stack_counter >= 0:
        bursts[int(stack[stack_counter]), 2] = offsets[n]
        stack_counter -= 1
    # print('bursts')
    # print(bursts)
    return bursts


# Call Word Calculation
def CalculateBurst(Keyword, Column):
    Connect()
    results = ExecuteAQuery(
        "MATCH(c:Column)-[]-> (k:Key) with c, k match (k:Key)-[]->(t:TimePoint) where k.name = '" + Keyword + "' and c.name = '" + Column + "' return t.name as time")
    # "MATCH (time:Timestamp) WITH time MATCH (time:Timestamp)-[]-(topic:Topic) WITH time, topic  MATCH (n:KeyWord)-[]-(p:Paper)-[]-(topic)-[]-(time) WHERE n.value = '"+Keyword+"' return distinct time.key as time")

    # convert the received list to aa array list
    offsets = []
    for index in results:
        offsets.append(int(index["time"]))

    print('ket qua truy van')
    print(offsets)
    if (offsets.__len__() <= 1):
        return

    # Count TimePoints of the keyword
    SumTimePointCal[0] += offsets.__len__()

    b = kleinberg(offsets, s=2, gamma=0.01)
    print('ket qua burst so khai')
    print(b)
    print('ket qua burst da xu ly')
    buff = b[0]
    ResultList = []
    for tuple in b:
        if tuple[0] == 1:
            if buff[0] != 0:
                print(buff)
                ResultList.append(str(buff[1]) + "-" + str(buff[2]))
            buff = tuple
        else:
            if buff[0] < tuple[0]:
                buff = tuple
    print(buff)
    ResultList.append(str(buff[1]) + "-" + str(buff[2]))

    # count number of burst
    SumBurstFoundCal[0] += ResultList.__len__()

    return ResultList
