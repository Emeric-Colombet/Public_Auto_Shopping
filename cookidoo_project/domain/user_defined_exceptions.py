from dataclasses import dataclass

@dataclass
class CustomerCreationException(Exception):
    message : str 

@dataclass
class CustomerAuthenticationException(Exception):
    message : str