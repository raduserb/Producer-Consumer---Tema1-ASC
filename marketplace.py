"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import logging
from logging.handlers import RotatingFileHandler
import threading
import time
import unittest
from .product import Coffee, Tea

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.producer_id = 0
        self.cart_id = 0
        self.queue_size_per_producer = queue_size_per_producer

        # tuple list that I use to map products with producer ids
        self.products = []
        # a dictionary that I use to map producer to their products
        self.producer_products = {}
        # a dictionary I use to map cart id to their products
        self.carts = {}

        # necessary locks
        self.add_to_cart_lock = Lock()
        self.remove_from_cart_lock = Lock()
        self.new_cart_lock = Lock()
        self.stdout_lock = Lock()

        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.INFO)
        self.handler = RotatingFileHandler("marketplace.log", maxBytes=1024 * 512, backupCount=20)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.formatter.converter = time.gmtime
        self.logger.addHandler(self.handler)


    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info("Registering producer")

        self.producer_id += 1

        # initializing the producer products with an empty list (just registered)
        self.producer_products[self.producer_id] = []

        self.logger.info("Producer registered with id %s",
                         self.producer_id )

        return self.producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        self.logger.info("Publishing product %s with producer_id %s ", product, producer_id)


        if len(self.producer_products[producer_id]) != self.queue_size_per_producer:
            # there is enough space to add the product to the list
            self.producer_products[producer_id].append(product)
            self.products.append((product, producer_id))
            self.logger.info("Product %s was published successfully", str(product))
            return True
        # not enogh space to add the product
        self.logger.info("Not enough space to publish product %s", str(product))
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info("Adding new_cart")
        with self.new_cart_lock:
            cart_id = self.cart_id + 1
            # initializing with an empty list for the products in the cart
            self.carts[cart_id] = []
            self.cart_id += 1

        self.logger.info("Created new cart with id %s", cart_id)

        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        self.logger.info("Adding product %s to cart %d", str(product), cart_id)

        with self.add_to_cart_lock:
            for product_iterator in self.products:
                # searching for the required product
                if product_iterator[0] == product:
                    # we found the required product and we remove it from the list
                    self.products.remove(product_iterator)
                    # we also remove it from the producers products
                    self.producer_products[product_iterator[1]].remove(product_iterator[0])\
                    # we add the product to the cart
                    self.carts[cart_id].append(product_iterator)
                    self.logger.info("Product %s added to cart %d.", str(product), cart_id)
                    return True
            self.logger.info("Error adding product %s to cart %d.", str(product), cart_id)
            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("Removing product %s from cart with id %d", str(product), cart_id)
        with self.remove_from_cart_lock:
            my_exit = 0 # we use this to check if we found the product
            for product_iterator in self.carts[cart_id]:
                if product_iterator[0] == product:
                    my_exit = 1 # product found
                    # removing the product
                    self.carts[cart_id].remove(product_iterator)
                    # adding the product to the producer again
                    self.producer_products[product_iterator[1]].append(product_iterator[0])
                    # adding the product to the list of products again
                    self.products.append(product_iterator)
                    break
            if my_exit == 0:
                # product not found
                return False
        self.logger.info("Removed product %s from cart with id %d successfully.",
                        str(product), cart_id)
        return True

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        self.logger.info("Placing order from cart with id %s.", str(cart_id))

        cart_products = self.carts.get(cart_id)
        if cart_products is None: # checking if there are any products
            return []

        with self.stdout_lock:
            for product, _ in cart_products:
                #printing the products
                print(threading.current_thread().getName() +  " bought " + str(product))

        del self.carts[cart_id]

        self.logger.info("Placed the order from the cart with id %s successfully", str(cart_id))

        return cart_products

class TestMarketplace(unittest.TestCase):
    """class used for unittesting"""
    def setUp(self):
        """setting up"""
        self.marketplace = Marketplace(4)
        self.product1 = Tea("Linden", "herbal", 9)
        self.product2 = Tea("Cactus fig", "Grenn", 3)
        self.product3 = Coffee("Arabica", "5.02", "MEDIUM", 9)

    def test_register_producer(self):
        """testing register_producer"""
        # producer id s start from 1
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)

    def test_publish(self):
        """testing publish"""
        producer_id = self.marketplace.register_producer()
        self.assertTrue(self.marketplace.publish(producer_id, self.product1))
        self.assertTrue(self.marketplace.publish(producer_id, self.product2))
        self.assertTrue(self.marketplace.publish(producer_id, self.product3))

    def test_new_cart(self):
        """testing new_cart"""
        cart_id_1 = self.marketplace.new_cart()
        cart_id_2 = self.marketplace.new_cart()

        # cart ids start from 1
        self.assertEqual(cart_id_1, 1)
        self.assertEqual(cart_id_2, 2)

    def test_add_to_cart(self):
        """testing add_to_cart"""
        producer_id_1 = self.marketplace.register_producer()
        producer_id_2 = self.marketplace.register_producer()

        self.marketplace.publish(producer_id_1, self.product1)
        self.marketplace.publish(producer_id_1, self.product2)
        self.marketplace.publish(producer_id_2, self.product3)

        cart_id = self.marketplace.new_cart()

        self.assertTrue(self.marketplace.add_to_cart(cart_id, self.product1))
        self.assertTrue(self.marketplace.add_to_cart(cart_id, self.product2))
        self.assertFalse(self.marketplace.add_to_cart(cart_id, self.product3))

    def test_remove_from_cart(self):
        """testing remove_from_cart"""
        cart_id = self.marketplace.new_cart()
        self.marketplace.add_to_cart(cart_id, self.product1)
        self.marketplace.add_to_cart(cart_id, self.product2)
        self.marketplace.add_to_cart(cart_id, self.product3)
        self.assertEqual(self.marketplace.remove_from_cart(cart_id, self.product2))

    def test_place_order(self):
        """testing place_order"""
        producer_id_1 = self.marketplace.register_producer()
        self.marketplace.publish(producer_id_1, self.product1)
        self.marketplace.publish(producer_id_1, self.product2)
        self.marketplace.publish(producer_id_1, self.product3)
        cart_id = self.marketplace.new_cart()
        self.marketplace.add_to_cart(cart_id, self.product1)
        self.marketplace.add_to_cart(cart_id, self.product3)
        self.assertEqual(self.marketplace.place_order(cart_id), [self.product1,self.product3])

if __name__ == '__main__':
    unittest.main()
