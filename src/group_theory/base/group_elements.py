from abc import ABC, abstractmethod
from functools import reduce

import math
import sympy
import numpy

class GroupElement(ABC):  
    @abstractmethod
    def get_order(self):
        pass
    
    @abstractmethod
    def is_identity(self):
        pass

class Permutation(GroupElement):
    def __init__(self, permutation: dict):
        self.permutation = permutation
        self.num_letters = len(self.permutation)

        # properties
        self._cycle_decomposition = None
        self._order = None
        self._sign = None

    def __repr__(self) -> str:
        self.cycle_notation = self.get_cycle_notation()
        return self.cycle_notation
    
    def __eq__(self,other):
        return self.permutation==other.permutation
    
    def __ne__(self,other):
        return ~self.__eq__(self,other)
    
    def __hash__(self):
        return hash(frozenset(self.permutation.items()))

    def __mul__(self, other):
        composition = {i:self.permutation[other.permutation[i]] for i in range(1,self.num_letters+1)}
        return Permutation(composition)
    
    def __pow__(self, N: int):
        if N==0:
            return Permutation({i:i for i in range(1,self.num_letters+1)})
        if N>0:
            return reduce(lambda x,y: x*y, [self]*N)
        if N<0:
            return reduce(lambda x,y: x*y, [~self]*abs(N))
    
    def __invert__(self):
        inverse = {self.permutation[k]:k for k in self.permutation.keys()}
        return Permutation(inverse)

    def find_cycle_dict(self, start: int):
        current_key = start
        cycle = {}
        while self.permutation[current_key]!= start:
            cycle[current_key]=self.permutation[current_key]
            current_key = self.permutation[current_key]
        cycle[current_key]=self.permutation[current_key]

        return cycle

    def get_cycle_notation(self):
        if self.is_identity():
            return "1"
        key_set = set(self.permutation.keys())
        updated_key_set = key_set
        cycle_list = []
        while len(updated_key_set)>0:
            for k in key_set:
                if k in updated_key_set:
                    cycle = self.find_cycle_dict(start=k)
                    if len(cycle)>1: # ignore cycles of the form (j)
                        s = "("+ " ".join([str(i) for i in cycle.keys()]) +")"
                        cycle_list.append(s)
                    updated_key_set = updated_key_set-set(cycle.keys())
        return "".join(cycle_list[::-1])

    
    def get_cycle_decomposition(self):
        key_set = set(self.permutation.keys())
        updated_key_set = key_set
        cycle_list = []
        while len(updated_key_set)>0:
            for k in key_set:
                if k in updated_key_set:
                    cycle = self.find_cycle_dict(start=k)
                    updated_key_set = updated_key_set-set(cycle.keys())
                    if len(cycle)>1:                
                        for i in set(self.permutation.keys())-set(cycle.keys()):
                            cycle[i] = i
                        cycle_list.append(Permutation(cycle))

        return cycle_list
    
    @property
    def cycle_decomposition(self):
        if self._cycle_decomposition == None:
            self._cycle_decomposition = self.get_cycle_decomposition()
            return self._cycle_decomposition
        else:
            return self._cycle_decomposition
        
    def get_order(self):
        count=1
        product = self
        while not product.is_identity():
            product = product*self
            count += 1
        return count

    @property
    def order(self):
        if self._order is None:
            self._order = self.get_order()
            return self._order
        else:
            return self._order
        
    @property
    def sign(self):
        if self._sign is None:
            self._sign = numpy.linalg.det(self.to_matrix().matrix)
            return self._sign
        else:
            return self._sign

    @staticmethod
    def validate_permutation(permutation: dict):
        permutation = dict(sorted(permutation.items()))
        assert list(permutation.keys()) == [i+1 for i in range(len(permutation))], f"Invalid permutation inputs: {permutation}"
        assert set(permutation.values()) == set([i+1 for i in range(len(permutation))]), f"Invalid permutation outputs: {permutation}"
        return permutation
    
    def is_transposition(self) -> bool:
        return len([i for i in self.permutation.keys() if i!=self.permutation[i]])==2
    
    def is_cycle(self):
        if len(self.cycle_decomposition)==1:
            return True
        else:
            return False
    
    def is_identity(self):
        return self.permutation == {i:i for i in range(1,self.num_letters+1)}
    
    def to_matrix(self):
        shape = (self.num_letters, self.num_letters)
        matrix = numpy.zeros(shape)
        for k in self.permutation.keys():
            matrix[k-1,self.permutation[k]-1]=1
        return Matrix(matrix, characteristic=2)

class ResidueClass(GroupElement):
    def __init__(self, residue: int,modulus: int):
        self.modulus = modulus
        self.residue = residue % modulus
        self.order = self.get_order()

    def __repr__(self):
        return "["+str(self.residue)+"]"
    
    def __hash__(self):
        return hash((self.residue,self.modulus))
    
    def __eq__(self,other):
        return (self.residue==other.residue) and (self.modulus==other.modulus)
    
    def __ne__(self,other):
        return ~self.__eq__(self,other)

    def __add__(self,other):
        if self.modulus!=other.modulus:
            raise ValueError('the moduli must be equal')
        else:
            return ResidueClass((self.residue+other.residue) % self.modulus, self.modulus)
        
    def __mul__(self,other):
        if self.modulus!=other.modulus:
            raise ValueError('the moduli must be equal')
        else:
            return ResidueClass((self.residue*other.residue) % self.modulus, self.modulus)
        
    def __pow__(self, N: int):
        if N==0:
            return ResidueClass(1, self.modulus)
        if N>0:
            return reduce(lambda x,y: x*y, [self]*N)
        if N<0:
            return reduce(lambda x,y: x*y, [~self]*abs(N))
    
    def __neg__(self):
        return ResidueClass(-self.residue,self.modulus)
    
    def __sub__(self,other):
        return self+(-other)

    def __invert__(self):
        if math.gcd(self.residue,self.modulus)!=1:
            raise ValueError('the residue and modulus must be relatively prime for a multiplicative inverse to exist')
        else:
            # this is Euler's theorem
            exp = sympy.totient(self.modulus)-1
            return ResidueClass(self.residue**exp,self.modulus)

    def get_order(self):
        pass
    
    def is_identity(self):
        pass

class AdditiveResidueClass(ResidueClass):
    def __init__(self, residue: int, modulus: int):
        super().__init__(residue, modulus)

    def __mul__(self,other):
        if self.modulus!=other.modulus:
            raise ValueError('the moduli must be equal')
        else:
            return AdditiveResidueClass((self.residue+other.residue) % self.modulus, self.modulus)
        
    def __pow__(self, N: int):
        if N==0:
            return AdditiveResidueClass(0, self.modulus)
        if N>0:
            return reduce(lambda x,y: x*y, [self]*N)
        if N<0:
            return reduce(lambda x,y: x*y, [~self]*abs(N))
        
    def __invert__(self):
        return AdditiveResidueClass(-self.residue,self.modulus)
        
    def get_order(self):
        return int(self.modulus/math.gcd(self.residue, self.modulus))

    def is_identity(self):
        if self.residue==0:
            return True
        else:
            return False

class MultiplicativeResidueClass(ResidueClass):
    def __init__(self, residue: int, modulus: int):
        super().__init__(residue, modulus)

    def __mul__(self,other):
        if self.modulus!=other.modulus:
            raise ValueError('the moduli must be equal')
        else:
            return MultiplicativeResidueClass((self.residue*other.residue) % self.modulus, self.modulus)

    def __pow__(self, N: int):
        if N==0:
            return MultiplicativeResidueClass(1, self.modulus)
        if N>0:
            return reduce(lambda x,y: x*y, [self]*N)
        if N<0:
            return reduce(lambda x,y: x*y, [~self]*abs(N))
        
    def __invert__(self):
        if math.gcd(self.residue,self.modulus)!=1:
            raise ValueError('the residue and modulus must be relatively prime for a multiplicative inverse to exist')
        else:
            # this is Euler's theorem
            exp = sympy.totient(self.modulus)-1
            return MultiplicativeResidueClass(self.residue**exp,self.modulus)
        
    def get_order(self):
        return int(self.modulus/math.gcd(self.residue, self.modulus))
        
    def is_identity(self):
        if self.residue==1:
            return True
        else:
            return False

class Matrix(GroupElement):
    def __init__(self, matrix: sympy.Matrix, characteristic: int):
        self.matrix = matrix % characteristic
        self.dimension = self.matrix.shape[0]
        self.characteristic = characteristic

    def __repr__(self):
        rep = self.matrix.__repr__()
        return rep

    def __eq__(self,other):
        return self.matrix==other.matrix
    
    def __hash__(self) -> int:
        return hash((tuple(self.matrix),self.characteristic))
    
    def __mul__(self,other):
        return Matrix((self.matrix*other.matrix) % self.characteristic, self.characteristic)

    def __invert__(self):
        return Matrix(self.matrix.inv_mod(self.characteristic), self.characteristic)

    def __pow__(self, N: int):
        if N==0:
            return Matrix(sympy.eye(self.dimension))
        if N>0:
            return reduce(lambda x,y: x*y, [self]*N)
        if N<0:
            return reduce(lambda x,y: x*y, [~self]*abs(N))

    def get_order(self):
        return 0
    
    def is_identity(self):
        return self.matrix==sympy.eye(self.dimension)