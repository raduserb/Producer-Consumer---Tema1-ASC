"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from time import sleep
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """

        # init with parameters
        Thread.__init__(self, **kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.producer_id = self.marketplace.register_producer()

    def run(self):
        while True:
            for product in self.products:
                # for each product
                product_id = product[0]
                quantity = product[1]
                product_wait_time = product[2]

                for _ in range(quantity):
                    #trying to publish the items
                    while not self.marketplace.publish(self.producer_id, product_id):
                        # wait until we can publish the product
                        sleep(self.republish_wait_time)
                    sleep(product_wait_time)
