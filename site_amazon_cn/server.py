from multiprocessing import Process, current_process, cpu_count
from spy import *

from item import *
from multiprocessing import Manager


class Crawler(object):
    def __init__(self, root, parser = None):
        self.root = root
        self.parser = spider_amazon_item(self.root)
        self.fetcher = NoCacheFetch(proxy = '127.0.0.1:8090')
        self.spider = Rolling(self.fetcher, self.parser.generater_item_index())
        self.run()

    def run(self):
        _runner = GSpider(self.spider, workers_count = 10)
        _runner.start()


def split_task_to_process(task_list, cores):
    for i in xrange(0, len(task_list), cores):
        yield task_list[i:i+cores]


if __name__ == "__main__":
    cores = 8
    mobile = ["http://www.amazon.cn/s/ref=sv_cps_%d"%x+'?ie=UTF8&page=1&rh=n%3A664978051%2Cn%3A665002051%2Cp_6%3AA1AJ19PSB66TGU%2Cp_n_feature_four_browse-bin%3A115583071%7C2147059051%7C2147061051%7C2147060051%7C2147058051%7C2147057051%7C80776071%7C115431071%7C115430071%7C2147062051%7C115434071%7C115433071' for x in range(1,12)]
    camera = ["http://www.amazon.cn/s/ref=sv_p_%d"%h+'?ie=UTF8&page=1&rh=n%3A2110347051' for h in range(2,13)]
    digital = ["http://www.amazon.cn/s/ref=sv_mp_%d"%d+'?ie=UTF8&page=1&rh=n%3A760236051' for d in range(2,14)]
    tv = ["http://www.amazon.cn/s/ref=sv_av_%d"%t+'?ie=UTF8&page=1&rh=n%3A874269051%2Cp_n_feature_two_browse-bin%3A2127962051' for t in range(3,12)]
    x =["http://www.amazon.cn/s/ref=sv_ma_4?ie=UTF8&page=1&rh=n%3A2121147051","http://www.amazon.cn/s/ref=sv_ma_5?ie=UTF8&page=1&rh=n%3A81948071","http://www.amazon.cn/s/ref=sv_ma_8?ie=UTF8&page=1&rh=n%3A2132895051"]
    q = ['http://www.amazon.cn/s/ref=sv_cps_1?ie=UTF8&page=1&rh=n%3A665002051%2Cp_n_feature_browse-bin%3A2045583051','http://www.amazon.cn/s/ref=sv_cps_3?ie=UTF8&page=1&rh=n%3A665002051%2Cp_n_feature_browse-bin%3A2045582051','http://www.amazon.cn/s/ref=sv_cps_4?ie=UTF8&page=1&rh=n%3A665002051%2Cp_n_feature_browse-bin%3A2045584051','http://www.amazon.cn/s/ref=sv_cps_1?ie=UTF8&page=1&rh=n%3A664978051%2Cn%3A665002051%2Cp_6%3AA1AJ19PSB66TGU%2Cp_n_feature_four_browse-bin%3A115583071%7C2147059051%7C2147061051%7C2147060051%7C2147058051%7C2147057051%7C80776071%7C115431071%7C115430071%7C2147062051%7C115434071%7C115433071','http://www.amazon.cn/s/ref=sv_cps_5?ie=UTF8&page=1&rh=n%3A665002051%2Cp_n_feature_browse-bin%3A2045580051','http://www.amazon.cn/s/ref=sv_cps_8?ie=UTF8&page=1&rh=n%3A665018051','http://www.amazon.cn/s/ref=sv_cps_9?ie=UTF8&page=1&rh=n%3A665016051','http://www.amazon.cn/s/ref=sv_cps_10?ie=UTF8&page=1&rh=n%3A665189051','http://www.amazon.cn/s/ref=sv_cps_11?ie=UTF8&page=1&rh=n%3A665017051']
    #task_list = ['http://www.360buy.com/products/652-828-843.html', 'http://www.360buy.com/products/652-829-854.html', 'http://www.360buy.com/products/652-830-868.html', 'http://www.360buy.com/products/652-829-846.html', 'http://www.360buy.com/products/652-653-655.html', 'http://www.360buy.com/products/652-829-847.html', 'http://www.360buy.com/products/652-830-861.html', 'http://www.360buy.com/products/652-828-838.html', 'http://www.360buy.com/products/652-6880-6881.html', 'http://www.360buy.com/products/652-828-837.html', 'http://www.360buy.com/products/652-654-836.html', 'http://www.360buy.com/products/652-829-848.html', 'http://www.360buy.com/products/652-654-832.html', 'http://www.360buy.com/products/652-828-1261.html', 'http://www.360buy.com/products/652-828-842.html', 'http://www.360buy.com/products/652-654-886.html', 'http://www.360buy.com/products/652-654-834.html', 'http://www.360buy.com/products/652-830-864.html', 'http://www.360buy.com/products/652-830-866.html', 'http://www.360buy.com/products/652-830-867.html', 'http://www.360buy.com/products/652-828-1274.html', 'http://www.360buy.com/products/652-829-845.html', 'http://www.360buy.com/products/652-828-844.html', 'http://www.360buy.com/products/652-830-863.html', 'http://www.360buy.com/products/652-828-962.html', 'http://www.360buy.com/products/652-6880-1195.html', 'http://www.360buy.com/products/652-654-835.html', 'http://www.360buy.com/products/652-829-851.html', 'http://www.360buy.com/products/652-653-659.html', 'http://www.360buy.com/products/652-6880-6882.html', 'http://www.360buy.com/products/652-830-862.html', 'http://www.360buy.com/products/652-828-839.html', 'http://www.360buy.com/products/652-829-1219.html', 'http://www.360buy.com/products/652-828-869.html', 'http://www.360buy.com/products/652-654-833.html', 'http://www.360buy.com/products/652-654-831.html', 'http://www.360buy.com/products/652-828-841.html']
    #task_list = ['http://www.360buy.com/products/737-794-870.html','http://www.360buy.com/products/737-794-1706.html','http://www.360buy.com/products/652-830-5003.html']
    task_list = set(mobile + camera + digital + tv + x + q)
    #for pt in split_task_to_process(task_list,cores):
    #    Process(target=Crawler, args=(pt,)).start()
    #Crawler(['http://www.360buy.com/products/737-794-870.html',])
    Crawler(task_list)





