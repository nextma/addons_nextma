# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 SISTHEO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#   AIM :
#           library to generate account codes
#
##############################################################################
# Date      Author      Description
# 20090603  SYLEAM/CB   modificators
#
##############################################################################
#   TECHNICAL DETAILS :
#        'code': fields.char('Code', size=64)
##############################################################################

import string


class Modificator(object):
    """
    TODO: describe this
    """
    def __init__(self, strVal):
        self.strVal = strVal

    def setval(self, strVal):
        self.strVal = strVal

    def rmspace(self):
        return self.strVal.strip()

    def strip(self):
        return self.strVal.strip()

    def rmponct(self):
        newval = self.strVal
        for i in range(len(string.punctuation)):
            newval = newval.replace(string.punctuation[i], '')
        return newval

    def rmaccent(self):
        #see also : from string import maketrans || string.translate
        newval = self.strVal.encode('utf-8')
        oldchar = "àäâéèëêïîöôüûùÿÄÂËÊÏÎÖÔÜÛ".decode('utf-8')
        newchar = "aaaeeeeiioouuuyAAEEIIOOUU"
        for i in range(len(oldchar)):
            newval = newval.replace(oldchar[i].encode('utf-8'), newchar[i])
        return newval

    def rmspe(self):
        allowed_chars = string.letters + string.digits
        return ''.join(c for c in self.strVal if c in allowed_chars)

    def truncate1(self):
        return self.strVal[:1]

    def truncate2(self):
        return self.strVal[:2]

    def truncate3(self):
        return self.strVal[:3]

    def truncate4(self):
        return self.strVal[:4]

    def truncate6(self):
        return self.strVal[:6]

    def truncate12(self):
        return self.strVal[:12]

    def charnum(self):
        first_letter = self.strVal[0]
        if first_letter.isalpha():
            num = ord(first_letter.upper()) - 64
            return ("%d" % num).zfill(2)
        else:
            return "00"

    def capitalize(self):
        return self.strVal.upper()

    def upper(self):
        return self.strVal.upper()

    def uppercase(self):
        return self.strVal.upper()

    def lower(self):
        return self.strVal.lower()

    def lowercase(self):
        return self.strVal.lower()

    def zfill2(self):
        """ Fill with 0 on the left. """
        return self.strVal.zfill(2)

    def zfill4(self):
        return self.strVal.zfill(4)

    def zfill6(self):
        return self.strVal.zfill(6)

    def rfill2(self):
        """ Fill with 0 on the right. """
        base_str = self.strVal[:2]
        compl = 2 - len(base_str)
        suffix = "0" * compl
        return base_str + suffix

    def rfill4(self):
        base_str = self.strVal[:4]
        compl = 4 - len(base_str)
        suffix = "0" * compl
        return base_str + suffix

    def rfill6(self):
        base_str = self.strVal[:6]
        compl = 6 - len(base_str)
        suffix = "0" * compl
        return base_str + suffix

if __name__ == '__main__':
    mod = Modificator('SYLEAM INFO SERVICES')
    print mod.truncate2()
    print mod.truncate4()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
