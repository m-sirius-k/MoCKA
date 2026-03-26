from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    def name(self): pass

    @abstractmethod
    def is_available(self): pass

    @abstractmethod
    def generate(self, request): pass
