"""
This module represents the Consumer.
Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.
        :type carts: List
        :param carts: a list of add and remove operations
        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace
        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available
        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """

        # init with parameters
        Thread.__init__(self,**kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time


    def run(self):
        for i in range(len(self.carts)):
            # getting a new cart id
            cart_id = self.marketplace.new_cart()

            for operation in self.carts[i]:
                #iterating through the operations
                for _ in range(operation.get("quantity")):
                    if operation.get("type") == "add":
                        # trying to add to cart and not stopping until i can
                        while not self.marketplace.add_to_cart(cart_id, operation.get("product")):
                            time.sleep(self.retry_wait_time) # wait until product is available
                    elif operation.get("type") == "remove":
                        # removing from cart
                        self.marketplace.remove_from_cart(cart_id, operation.get("product"))

            self.marketplace.place_order(cart_id)
    