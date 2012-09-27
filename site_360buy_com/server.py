from multiprocessing import Process, current_process, cpu_count
from spy import *

from item import *
from multiprocessing import Manager


class Crawler(object):
    def __init__(self, root, parser = None):
        self.root = root
        self.parser = spider_360_item(self.root)
        self.fetcher = NoCacheFetch(char = 'gb18030', proxy = '127.0.0.1:8090')
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
    task_list = ['http://www.360buy.com/products/652-828-843.html', 'http://www.360buy.com/products/652-829-854.html', 'http://www.360buy.com/products/652-830-868.html', 'http://www.360buy.com/products/652-829-846.html', 'http://www.360buy.com/products/652-653-655.html', 'http://www.360buy.com/products/652-829-847.html', 'http://www.360buy.com/products/652-830-861.html', 'http://www.360buy.com/products/652-828-838.html', 'http://www.360buy.com/products/652-6880-6881.html', 'http://www.360buy.com/products/652-828-837.html', 'http://www.360buy.com/products/652-654-836.html', 'http://www.360buy.com/products/652-829-848.html', 'http://www.360buy.com/products/652-654-832.html', 'http://www.360buy.com/products/652-828-1261.html', 'http://www.360buy.com/products/652-828-842.html', 'http://www.360buy.com/products/652-654-886.html', 'http://www.360buy.com/products/652-654-834.html', 'http://www.360buy.com/products/652-830-864.html', 'http://www.360buy.com/products/652-830-866.html', 'http://www.360buy.com/products/652-830-867.html', 'http://www.360buy.com/products/652-828-1274.html', 'http://www.360buy.com/products/652-829-845.html', 'http://www.360buy.com/products/652-828-844.html', 'http://www.360buy.com/products/652-830-863.html', 'http://www.360buy.com/products/652-828-962.html', 'http://www.360buy.com/products/652-6880-1195.html', 'http://www.360buy.com/products/652-654-835.html', 'http://www.360buy.com/products/652-829-851.html', 'http://www.360buy.com/products/652-653-659.html', 'http://www.360buy.com/products/652-6880-6882.html', 'http://www.360buy.com/products/652-830-862.html', 'http://www.360buy.com/products/652-828-839.html', 'http://www.360buy.com/products/652-829-1219.html', 'http://www.360buy.com/products/652-828-869.html', 'http://www.360buy.com/products/652-654-833.html', 'http://www.360buy.com/products/652-654-831.html', 'http://www.360buy.com/products/652-828-841.html']
    #task_list = ['http://www.360buy.com/products/737-794-870.html','http://www.360buy.com/products/737-794-1706.html','http://www.360buy.com/products/652-830-5003.html']
    for pt in split_task_to_process(task_list,cores):
        Process(target=Crawler, args=(pt,)).start()
    #Crawler(['http://www.360buy.com/products/737-794-870.html',])





