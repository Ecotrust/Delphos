#===============================================================================
# Delphos - a decision-making tool for community-based marine conservation.
# 
# @copyright	2007 Ecotrust
# @author		Tim Welch
# @contact		twelch at ecotrust dot org
# @license		GNU GPL 2 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  The full license for this distribution
# has been made available in the file LICENSE.txt
#
# $Id$
#
# @summary - defines common functions used throughout Delphos
#===============================================================================

import time
import datetime

def strIsInt(str):
    """Test given string is an integer
    """
    if str == None:
        return False
    
    try:
        num = int(str)
    except ValueError:
        return False
    return True

def initialize_float_array(rows, cols):
    """Allocates a lists of lists of the given dimension with type float
    """
    mat = []
    for x in range(rows):
        mat.append([0.0] * cols)
    return mat

def initialize_int_array(rows, cols):
    """Allocates a lists of lists of the given dimension with type int
    """
    mat = []
    for x in range(rows):
        mat.append([0] * cols)
    return mat

def initialize_str_array(rows, cols):
    """Allocates a lists of lists of the given dimension with type int
    """
    mat = []
    for x in range(rows):
        mat.append([""] * cols)
    return mat

def utc_to_local_time(x):
    """Given a UTC datetime object x set to GMT, convert it to the local time
    """
    offset = datetime.timedelta( hours=(time.altzone/3600) )
    return x - offset