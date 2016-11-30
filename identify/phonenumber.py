__author__ = 'Monte'

import sys


class PhoneNumber(object):
    def __init__(self, phn):
        self.phn = phn
        self.number = ""

    def valid_numbers(self):
        # Invokes a validating method with respect to the supplied object type 
        if isinstance(self.phn, list) or isinstance(self.phn, tuple):
            self.list_validator(self.phn)
        elif isinstance(self.phn, long):
            self.integer_validator(self.phn)
        elif isinstance(self.phn, int):
            self.integer_validator(self.phn)
        elif isinstance(self.phn, str) or isinstance(self.phn, unicode):
            self.string_validator(self.phn)
        else:
            # print >>sys.stderr, "Phone number ", self.phn, "is of an invalid phone number type", type(self.phn)
            return
        return self.phn

    def list_validator(self, the_list):
        """ Validates phone numbers in a list """
        valid_list = []
        for _number in the_list:
            if self.validator(_number):
                valid_list.append(self.validator(_number))
        self.phn = valid_list

    def integer_validator(self, the_int):
        """ Validates phone number supplied as an integer """

        self.phn = self.validator(the_int)

    def string_validator(self, the_str):
        """ Validates phone number supplied as a string"""

        the_str = str(the_str).replace("-", '').replace("(", '').replace(")", '').replace(" ", '')

        self.phn = self.validator(the_str)

    def validator(self, number):
        """ Validates the phone number and returns a phone number with a  +254 suffix"""

        # Try convert the phone number to a string if its in any other object(data) type
        self.number = number
        if isinstance(number, str):
            pass
        else:
            try:
                number = str(number)
            except ValueError:
                print >>sys.stderr, "Invalid phone number data type"
                return

        # Remove white spaces from the phone number
        number = number.replace(' ', "")

        def clean(arg):
            """ Validates the character given with respect to accepted characters in a phone number"""
            return arg in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+"]

        def validate_length(arg):
            """ Returns a valid phone number or """
            _number = arg
            length = len(_number)
            if length < 9:
                self.number = ""
            elif length == 9:
                if _number[:1] == "0":
                    print >>sys.stderr, _number, "has less values"
                    self.number = ""
            elif length == 10:
                if _number[0] == "0":
                    self.number = _number[1:]
                else:
                    print >>sys.stderr, "Invalid suffix for a phone _number"
                    self.number = ""
            elif length == 12:
                if _number[:3] == "254":
                    self.number = _number[3:]
                else:
                    print >>sys.stderr, "Invalid suffix or too much characters for a phone _number"
                    _number = ""
            elif length == 13:
                if _number[:4] == "+254":
                    pass
                else:
                    print sys.stderr, "Invalid suffix or too much characters for a phone _number"
                    _number = ''
            else:
                print >>sys.stderr, "Unspecified error"
                _number = ""

        # Remove invalid characters in the phone number
        self.number = filter(clean, str(number))

        # Validate the phone numbers length
        validate_length(self.number)

        if len(self.number) == 13:
            return self.number
        elif len(self.number) == 9:
            return "%s%s" % ("+254", self.number)
        else:
            return


class InvalidPhoneNumberTypeException(Exception):
    """
    Raised when a phone number cannot be converted to a string
    """
    def __init__(self, message=None):
        if not message:
            self.message = "Invalid phone number data type"
        Exception.__init__(self)
