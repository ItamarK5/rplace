
def inita(self):
    super(type(self), self).__init__()
    print(self.__class__.__name__)


class A(object):
    def __init_subclass__(cls, **kwargs):
        cls.__init__ = inita
    def __init__(self):
        super().__init__()
        print(A)

class B(A):
    pass

class C(A):
    pass

class D(B,C):
    pass

class E(A):
    pass

class F(A):
    pass

class G(A,B):
    pass

class K(F,G,D):
    pass

K()