import gc
import crochet
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

from common import repository as R
from core.models import GenerateAbstractParams, AbstractModel
from spider.spider.spiders.google import GoogleSpider
from generator.facade import GeneratorFacade


crochet.setup()


class CoreService():
    crawler_runner = CrawlerRunner()

    @crochet.run_in_reactor
    def get_related_pages(self, phrase: str, page_number: int):
        R.SEARCH_PHRASE = phrase
        R.TARGET_PAGE_NUMBER = page_number

        dispatcher.connect(self.observe_results, signal=signals.item_scraped)
        self.crawler_runner.crawl(GoogleSpider)

    def observe_results(self, item: dict):
        R.RESULT_PAGES.append(dict(item))

    def generate_abstract(self, params: GenerateAbstractParams) -> AbstractModel:
        self.cleanup()
        self.get_related_pages(params.phrase, params.page_number)

        while not R.SPIDER_FINISHED:
            pass

        corpus = [page['content'] for page in R.RESULT_PAGES]

        answer, summary = GeneratorFacade.generate_abstract(params.phrase, corpus, params.answer_model, params.summary_model)
        abstract = AbstractModel(
            answer=answer,
            summary=summary
        )

        self.cleanup()

        return abstract

    def cleanup(self):
        R.SPIDER_FINISHED = False
        R.RESULT_PAGES = []
        gc.collect()
