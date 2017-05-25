import urllib
from datetime import datetime
import sys


def parse_data(x):
    
    idx= x[0] 
    url= x[1]
    tdate = x[2]
    right=x[3]
    lower_bound = x[4]
    upper_bound = x[5]
    ln = urllib.urlopen(url).readlines()
    months = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 
              'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
    

    volumes= map(lambda x: ('%s%s' % (x[4:6], months[x[0:3]]), 
                            int(x[8:13]), x[14:15], int(x[70:80])), filter(lambda x:x[0:3] in list(months.keys()), ln))
#     for t in volumes:
#         print t
    
    
    
    #xc_minus1p = filter(lambda x: x[1] < idx and x[1] > idx * 0.99, volumes)
    opt_range = filter(lambda x: x[1] > idx * lower_bound and x[1] < idx * upper_bound, volumes)#     for t in xc_minus2p:
#         print t
    
    opt_range_set = set(map(lambda x:x[0], opt_range))
    print opt_range
#     print opt_range_set
 
    opt_on_day =[]
    for m in opt_range_set:
        #print reduce(lambda x,y:x[3]+y[3], filter(lambda x: x[0] == m and x[2] == 'P' , xc_minus2p))
        
        f1= map(lambda x:x[3], filter(lambda x: x[0] == m and x[2] == right , opt_range))
        
        opt_on_day.append((tdate, m, reduce(lambda x,y:x+y, f1)))
        opt_on_day = sorted(opt_on_day)
    return opt_on_day


def day_series(sname, s1, head=False):
    if head:
        print "['series', %s]," % ''.join("'%s'," % v[0] for v in s1) 
    print "['%s', %s]," % (sname, ''.join('%d,' % v[1] for v in s1))
    
def donut(s1, s2): 
    print "['Right', 'Num Contracts'],"
    print "['Call', %d], ['Put', %d]," % (s1, s2)


def gen_dd(x):
    print "['%s', %s]," % ('series', ''.join("'%s'," % v[1] for v in x[0]))
    len1 = len(x[0])
    for a in sorted(x):
        #print "['%s', %s]," % (sumC[0][0][0], ''.join('%d,' % v[2] for v in sumC[0]))
        print "['%s', %s]," % (a[0][0], ''.join('%d,' % v[2] for v in a[0:len1]))

def generate_run_config():
#         'Apr 28, 2017',24615.13),
#             ('Apr 27, 2017',24698.48),
#             ('Apr 26, 2017',24578.43),
#             ('Apr 25, 2017',24455.94),
#             ('Apr 24, 2017',24139.48),
#             ('Apr 21, 2017',24042.02),
#             ('Apr 20, 2017',24056.98),
#             ('Apr 19, 2017',23825.88),
#             ('Apr 18, 2017',23924.54),
#             ('Apr 13, 2017',24261.66),
#             ('Apr 12, 2017',24313.5),
#             ('Apr 11, 2017',24088.46),
#             ('Apr 10, 2017',24262.18),
#             ('Apr 7, 2017',24267.3),
#             ('Apr 6, 2017',24273.72),
#             ('Apr 5, 2017',24400.8),
#             ('Apr 3, 2017',24261.48),

    
    hsi = [
            ('May 23, 2017',25403.15),
            ('May 22, 2017',25391.34),
            ('May 19, 2017',25174.87),
            ('May 18, 2017',25136.52),
            ('May 17, 2017',25293.63),
            ('May 16, 2017',25335.94),
            ('May 15, 2017',25371.59),
            ('May 12, 2017',25156.34),
            ('May 11, 2017',25125.55),
            ('May 10, 2017',25015.42),
            ('May 9, 2017',24889.03),
            ('May 8, 2017',24577.91),
            ('May 5, 2017',24476.35),
            ('May 4, 2017',24683.88),
            ('May 2, 2017',24696.13),

            ]

    url = 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio%s.htm'
    for e in hsi:
        print url % datetime.strptime(e[0], '%b %d, %Y').strftime('%y%m%d')
    
    run1 = sorted(map(lambda x: (x[1], datetime.strptime(x[0], '%b %d, %Y').strftime('%y%m%d'),  
                   url % datetime.strptime(x[0], '%b %d, %Y').strftime('%y%m%d')), hsi))

    lower_bound = 0.995
    upper_bound = 1.005
    # (index, url, tdate, right, lower_bound, upper_bound)
    
    runC=  map(lambda x:(x[0], x[2], x[1], 'C', lower_bound, upper_bound, ), run1)
    runP=  map(lambda x:(x[0], x[2], x[1], 'P', lower_bound, upper_bound, ), run1)
 
    print runC   
    # (tdate, opt_month, num_contracts)    
    #sumC = map(parse_data, runC)    
    sumC = [[('170419', '1704', 1528), ('170419', '1705', 335), ('170419', '1706', 296), ('170419', '1707', 64), ('170419', '1709', 855), ('170419', '1712', 805), ('170419', '1803', 0)], [('170418', '1704', 1513), ('170418', '1705', 1019), ('170418', '1706', 1322), ('170418', '1707', 229), ('170418', '1709', 1499), ('170418', '1712', 4578), ('170418', '1803', 0), ('170418', '1806', 839), ('170418', '1812', 3008), ('170418', '1906', 100), ('170418', '1912', 120), ('170418', '2006', 22)], [('170421', '1704', 1589), ('170421', '1705', 1454), ('170421', '1706', 1404), ('170421', '1707', 237), ('170421', '1709', 1495), ('170421', '1712', 4559), ('170421', '1803', 0), ('170421', '1806', 839), ('170421', '1812', 3258), ('170421', '1906', 100), ('170421', '1912', 120), ('170421', '2006', 22)], [('170420', '1704', 1618), ('170420', '1705', 1344), ('170420', '1706', 1357), ('170420', '1707', 237), ('170420', '1709', 1499), ('170420', '1712', 4579), ('170420', '1803', 0), ('170420', '1806', 839), ('170420', '1812', 3008), ('170420', '1906', 100), ('170420', '1912', 120), ('170420', '2006', 22)], [('170411', '1704', 4657), ('170411', '1705', 1884), ('170411', '1706', 1709), ('170411', '1707', 258), ('170411', '1709', 1907), ('170411', '1712', 6271), ('170411', '1803', 0), ('170411', '1806', 831), ('170411', '1812', 3008), ('170411', '1906', 100), ('170411', '1912', 120), ('170411', '2006', 22)], [('170424', '1704', 3703), ('170424', '1705', 1453), ('170424', '1706', 666), ('170424', '1707', 31), ('170424', '1709', 795), ('170424', '1712', 1644), ('170424', '1803', 0)], [('170403', '1704', 2478), ('170403', '1705', 931), ('170403', '1706', 256), ('170403', '1707', 0), ('170403', '1709', 557), ('170403', '1712', 1353), ('170403', '1803', 0)], [('170413', '1704', 3322), ('170413', '1705', 1255), ('170413', '1706', 430), ('170413', '1707', 28), ('170413', '1709', 558), ('170413', '1712', 1628), ('170413', '1803', 0)], [('170410', '1704', 3391), ('170410', '1705', 1087), ('170410', '1706', 393), ('170410', '1707', 28), ('170410', '1709', 558), ('170410', '1712', 1628), ('170410', '1803', 0)], [('170407', '1704', 3429), ('170407', '1705', 1098), ('170407', '1706', 355), ('170407', '1707', 25), ('170407', '1709', 558), ('170407', '1712', 1628), ('170407', '1803', 0)], [('170406', '1704', 2617), ('170406', '1705', 1028), ('170406', '1706', 359), ('170406', '1707', 13), ('170406', '1709', 559), ('170406', '1712', 1478), ('170406', '1803', 0)], [('170412', '1704', 6152), ('170412', '1705', 1966), ('170412', '1706', 1306), ('170412', '1707', 101), ('170412', '1709', 688), ('170412', '1712', 3298), ('170412', '1803', 0)], [('170405', '1704', 2175), ('170405', '1705', 585), ('170405', '1706', 547), ('170405', '1707', 67), ('170405', '1709', 105), ('170405', '1712', 1670), ('170405', '1803', 0)], [('170425', '1704', 2639), ('170425', '1705', 1209), ('170425', '1706', 1107), ('170425', '1707', 73), ('170425', '1709', 101), ('170425', '1712', 1766), ('170425', '1803', 0)], [('170505', '1705', 1586), ('170505', '1706', 1446), ('170505', '1707', 80), ('170505', '1708', 0), ('170505', '1709', 105), ('170505', '1712', 1767), ('170505', '1803', 0)], [('170508', '1705', 2736), ('170508', '1706', 1078), ('170508', '1707', 99), ('170508', '1708', 30), ('170508', '1709', 60), ('170508', '1712', 1711), ('170508', '1803', 2)], [('170426', '1704', 2681), ('170426', '1705', 1738), ('170426', '1706', 1014), ('170426', '1707', 41), ('170426', '1709', 56), ('170426', '1712', 1710), ('170426', '1803', 2)], [('170428', '1705', 2334), ('170428', '1706', 1072), ('170428', '1707', 49), ('170428', '1708', 0), ('170428', '1709', 57), ('170428', '1712', 1710), ('170428', '1803', 2)], [('170504', '1705', 4448), ('170504', '1706', 3071), ('170504', '1707', 268), ('170504', '1708', 149), ('170504', '1709', 185), ('170504', '1712', 1728), ('170504', '1803', 2)], [('170502', '1705', 4324), ('170502', '1706', 2954), ('170502', '1707', 202), ('170502', '1708', 68), ('170502', '1709', 185), ('170502', '1712', 1726), ('170502', '1803', 2)], [('170427', '1704', 3531), ('170427', '1705', 3213), ('170427', '1706', 2707), ('170427', '1707', 169), ('170427', '1709', 185), ('170427', '1712', 1726), ('170427', '1803', 2)], [('170509', '1705', 5518), ('170509', '1706', 3983), ('170509', '1707', 502), ('170509', '1708', 134), ('170509', '1709', 336), ('170509', '1712', 1869), ('170509', '1803', 57), ('170509', '1806', 54), ('170509', '1812', 311), ('170509', '1906', 0), ('170509', '1912', 15), ('170509', '2006', 12)], [('170510', '1705', 2958), ('170510', '1706', 2074), ('170510', '1707', 727), ('170510', '1708', 15), ('170510', '1709', 508), ('170510', '1712', 1848), ('170510', '1803', 57), ('170510', '1806', 54), ('170510', '1812', 311), ('170510', '1906', 0), ('170510', '1912', 15), ('170510', '2006', 12)], [('170511', '1705', 6016), ('170511', '1706', 3462), ('170511', '1707', 991), ('170511', '1708', 20), ('170511', '1709', 615), ('170511', '1712', 1859), ('170511', '1803', 57), ('170511', '1806', 54), ('170511', '1812', 1911), ('170511', '1906', 0), ('170511', '1912', 15), ('170511', '2006', 12)], [('170518', '1705', 2805), ('170518', '1706', 2106), ('170518', '1707', 293), ('170518', '1708', 34), ('170518', '1709', 107), ('170518', '1712', 10), ('170518', '1803', 600)], [('170512', '1705', 3116), ('170512', '1706', 1376), ('170512', '1707', 268), ('170512', '1708', 4), ('170512', '1709', 106), ('170512', '1712', 10), ('170512', '1803', 0)], [('170519', '1705', 3147), ('170519', '1706', 2112), ('170519', '1707', 299), ('170519', '1708', 34), ('170519', '1709', 381), ('170519', '1712', 12), ('170519', '1803', 600)], [('170517', '1705', 5749), ('170517', '1706', 3120), ('170517', '1707', 672), ('170517', '1708', 65), ('170517', '1709', 534), ('170517', '1712', 83), ('170517', '1803', 602)], [('170516', '1705', 3234), ('170516', '1706', 994), ('170516', '1707', 380), ('170516', '1708', 29), ('170516', '1709', 427), ('170516', '1712', 73), ('170516', '1803', 2)], [('170515', '1705', 3143), ('170515', '1706', 943), ('170515', '1707', 306), ('170515', '1708', 29), ('170515', '1709', 427), ('170515', '1712', 73), ('170515', '1803', 2)], [('170522', '1705', 3378), ('170522', '1706', 1249), ('170522', '1707', 402), ('170522', '1708', 30), ('170522', '1709', 427), ('170522', '1712', 76), ('170522', '1803', 2)], [('170523', '1705', 3109), ('170523', '1706', 1297), ('170523', '1707', 402), ('170523', '1708', 31), ('170523', '1709', 450), ('170523', '1712', 81), ('170523', '1803', 2)]]
    print sumC
    print '>>>BEGIN COPY'
    gen_dd(sumC)
    print '<<<END COPY'
    
    sumP = map(parse_data, runP)
    #sumP = [[('170419', '1704', 3077), ('170419', '1705', 846), ('170419', '1706', 443), ('170419', '1707', 70), ('170419', '1709', 860), ('170419', '1712', 710), ('170419', '1803', 0)], [('170418', '1704', 3327), ('170418', '1705', 1603), ('170418', '1706', 466), ('170418', '1707', 266), ('170418', '1709', 1203), ('170418', '1712', 5102), ('170418', '1803', 2), ('170418', '1806', 785), ('170418', '1812', 3015), ('170418', '1906', 100), ('170418', '1912', 100), ('170418', '2006', 0)], [('170421', '1704', 3089), ('170421', '1705', 1710), ('170421', '1706', 377), ('170421', '1707', 265), ('170421', '1709', 1203), ('170421', '1712', 5093), ('170421', '1803', 2), ('170421', '1806', 785), ('170421', '1812', 3275), ('170421', '1906', 100), ('170421', '1912', 100), ('170421', '2006', 0)], [('170420', '1704', 3169), ('170420', '1705', 1635), ('170420', '1706', 382), ('170420', '1707', 265), ('170420', '1709', 1203), ('170420', '1712', 5102), ('170420', '1803', 2), ('170420', '1806', 785), ('170420', '1812', 3015), ('170420', '1906', 100), ('170420', '1912', 100), ('170420', '2006', 0)], [('170411', '1704', 7223), ('170411', '1705', 2144), ('170411', '1706', 735), ('170411', '1707', 271), ('170411', '1709', 1565), ('170411', '1712', 6679), ('170411', '1803', 2), ('170411', '1806', 785), ('170411', '1812', 3015), ('170411', '1906', 100), ('170411', '1912', 100), ('170411', '2006', 0)], [('170424', '1704', 3993), ('170424', '1705', 752), ('170424', '1706', 1130), ('170424', '1707', 5), ('170424', '1709', 512), ('170424', '1712', 1625), ('170424', '1803', 0)], [('170403', '1704', 3454), ('170403', '1705', 526), ('170403', '1706', 116), ('170403', '1707', 0), ('170403', '1709', 511), ('170403', '1712', 1350), ('170403', '1803', 0)], [('170413', '1704', 4221), ('170413', '1705', 688), ('170413', '1706', 271), ('170413', '1707', 5), ('170413', '1709', 512), ('170413', '1712', 1625), ('170413', '1803', 0)], [('170410', '1704', 3768), ('170410', '1705', 676), ('170410', '1706', 260), ('170410', '1707', 5), ('170410', '1709', 512), ('170410', '1712', 1625), ('170410', '1803', 0)], [('170407', '1704', 3725), ('170407', '1705', 672), ('170407', '1706', 260), ('170407', '1707', 3), ('170407', '1709', 512), ('170407', '1712', 1625), ('170407', '1803', 0)], [('170406', '1704', 3732), ('170406', '1705', 649), ('170406', '1706', 262), ('170406', '1707', 3), ('170406', '1709', 512), ('170406', '1712', 1475), ('170406', '1803', 0)], [('170412', '1704', 4934), ('170412', '1705', 1186), ('170412', '1706', 297), ('170412', '1707', 13), ('170412', '1709', 547), ('170412', '1712', 3161), ('170412', '1803', 0)], [('170405', '1704', 979), ('170405', '1705', 461), ('170405', '1706', 13), ('170405', '1707', 8), ('170405', '1709', 35), ('170405', '1712', 1536), ('170405', '1803', 0)], [('170425', '1704', 2013), ('170425', '1705', 583), ('170425', '1706', 28), ('170425', '1707', 9), ('170425', '1709', 36), ('170425', '1712', 1586), ('170425', '1803', 0)], [('170505', '1705', 2554), ('170505', '1706', 556), ('170505', '1707', 17), ('170505', '1708', 25), ('170505', '1709', 37), ('170505', '1712', 1586), ('170505', '1803', 0)], [('170508', '1705', 939), ('170508', '1706', 637), ('170508', '1707', 26), ('170508', '1708', 32), ('170508', '1709', 15), ('170508', '1712', 1475), ('170508', '1803', 0)], [('170426', '1704', 1167), ('170426', '1705', 152), ('170426', '1706', 615), ('170426', '1707', 15), ('170426', '1709', 0), ('170426', '1712', 1475), ('170426', '1803', 0)], [('170428', '1705', 692), ('170428', '1706', 615), ('170428', '1707', 15), ('170428', '1708', 0), ('170428', '1709', 1), ('170428', '1712', 1475), ('170428', '1803', 0)], [('170504', '1705', 989), ('170504', '1706', 1158), ('170504', '1707', 21), ('170504', '1708', 34), ('170504', '1709', 15), ('170504', '1712', 1475), ('170504', '1803', 2)], [('170502', '1705', 972), ('170502', '1706', 1171), ('170502', '1707', 21), ('170502', '1708', 32), ('170502', '1709', 10), ('170502', '1712', 1475), ('170502', '1803', 2)], [('170427', '1704', 1873), ('170427', '1705', 513), ('170427', '1706', 1121), ('170427', '1707', 15), ('170427', '1709', 0), ('170427', '1712', 1475), ('170427', '1803', 2)], [('170509', '1705', 639), ('170509', '1706', 537), ('170509', '1707', 2), ('170509', '1708', 1), ('170509', '1709', 3), ('170509', '1712', 52), ('170509', '1803', 6), ('170509', '1806', 0), ('170509', '1812', 22), ('170509', '1906', 0), ('170509', '1912', 10), ('170509', '2006', 0)], [('170510', '1705', 542), ('170510', '1706', 36), ('170510', '1707', 1), ('170510', '1708', 6), ('170510', '1709', 0), ('170510', '1712', 52), ('170510', '1803', 12), ('170510', '1806', 0), ('170510', '1812', 10), ('170510', '1906', 0), ('170510', '1912', 10), ('170510', '2006', 0)], [('170511', '1705', 1165), ('170511', '1706', 108), ('170511', '1707', 1), ('170511', '1708', 6), ('170511', '1709', 0), ('170511', '1712', 52), ('170511', '1803', 14), ('170511', '1806', 0), ('170511', '1812', 1608), ('170511', '1906', 0), ('170511', '1912', 33), ('170511', '2006', 0)], [('170518', '1705', 1183), ('170518', '1706', 779), ('170518', '1707', 12), ('170518', '1708', 0), ('170518', '1709', 5), ('170518', '1712', 0), ('170518', '1803', 602)], [('170512', '1705', 695), ('170512', '1706', 25), ('170512', '1707', 0), ('170512', '1708', 0), ('170512', '1709', 0), ('170512', '1712', 0), ('170512', '1803', 2)], [('170519', '1705', 1340), ('170519', '1706', 785), ('170519', '1707', 12), ('170519', '1708', 0), ('170519', '1709', 355), ('170519', '1712', 0), ('170519', '1803', 603)], [('170517', '1705', 1519), ('170517', '1706', 823), ('170517', '1707', 10), ('170517', '1708', 0), ('170517', '1709', 0), ('170517', '1712', 0), ('170517', '1803', 610)], [('170516', '1705', 416), ('170516', '1706', 25), ('170516', '1707', 0), ('170516', '1708', 0), ('170516', '1709', 0), ('170516', '1712', 0), ('170516', '1803', 8)], [('170515', '1705', 275), ('170515', '1706', 21), ('170515', '1707', 0), ('170515', '1708', 0), ('170515', '1709', 0), ('170515', '1712', 0), ('170515', '1803', 8)], [('170522', '1705', 766), ('170522', '1706', 84), ('170522', '1707', 2), ('170522', '1708', 0), ('170522', '1709', 0), ('170522', '1712', 0), ('170522', '1803', 8)], [('170523', '1705', 751), ('170523', '1706', 157), ('170523', '1707', 2), ('170523', '1708', 0), ('170523', '1709', 56), ('170523', '1712', 0), ('170523', '1803', 8)]]
    
    print sumP
    print '>>>BEGIN COPY'
    gen_dd(sumP)
    print '<<<END COPY'
#     print "['%s', %s]," % ('series', ''.join("'%s'," % v[1] for v in sumC[0]))
#     len1 = len(sumC[0])
#     for a in sorted(sumC):
#         #print "['%s', %s]," % (sumC[0][0][0], ''.join('%d,' % v[2] for v in sumC[0]))
#         print "['%s', %s]," % (a[0][0], ''.join('%d,' % v[2] for v in a[0:len1]))
    cpr = []
    for i in range(len(sumC)):
        for j in range(len(sumC[i])):
            print 
    
    print cpr 
if __name__ == "__main__":
    
    generate_run_config()
    sys.exit()
    
    
    m1 = parse_data(24261, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170403.htm', 'C')
    m2 = parse_data(24267, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170407.htm', 'C')
    m3 = parse_data(24263, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170413.htm', 'C')       
    m4 = parse_data(23924, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170418.htm', 'C')
    m5 = parse_data(24615, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170426.htm', 'C')    
    print m1
    print m2
    day_series('24261', m1, True)
    day_series('24267', m2[0:len(m1)])
    day_series('24263', m3[0:len(m1)])
    day_series('23924', m4[0:len(m1)])
    day_series('24615', m5[0:len(m1)])

    n1 = parse_data(24261, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170403.htm', 'P')
    n2 = parse_data(24267, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170407.htm', 'P')
    n3 = parse_data(24263, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170413.htm', 'P')       
    n4 = parse_data(23924, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170418.htm', 'P')
    n5 = parse_data(24615, 'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio170426.htm', 'P')   
    print n1
    print n2
    day_series('24261', n1, True)
    day_series('24267', n2[0:len(m1)])
    day_series('24263', n3[0:len(m1)])
    day_series('23924', n4[0:len(m1)])
    day_series('24615', n5[0:len(m1)])
    
    donut(m3[0][1], n3[0][1])
    donut(m4[0][1], n4[0][1])
    donut(m5[0][1], n5[0][1])
    #
    # plot stuff
    #https://jsfiddle.net/t7bvbqk0/1/
    #
    #
    # retrieve historical index data 
    #https://www.google.com/finance/historical?cid=13414271&startdate=Apr+3%2C+2017&enddate=May+1%2C+2017&num=30&ei=p0chWfnMA8yC0AST-5qoCQ
    
#     dd1= map(lambda i:(m02[i][0], m15[i][1]-m02[i][1], "['%s-02', '%s-16', %d]," % (m02[i][0], m02[i][0], m15[i][1])), range(len(m02)))
#     print dd1
#     dd2 = map(lambda x:x[2], dd1)
#     print ''.join(x for x in dd2)
