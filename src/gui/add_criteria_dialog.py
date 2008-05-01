#===============================================================================
# Delphos - a decision-making tool for community-based marine conservation.
# 
# @copyright    2007 Ecotrust
# @author        Tim Welch
# @contact        twelch at ecotrust dot org
# @license        GNU GPL 2 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  The full license for this distribution
# has been made available in the file LICENSE.txt
#
# $Id$
#
# @summary - 
#===============================================================================

import os
import re
from os import path

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from util.common_functions import *

from delphos_exceptions import *
from add_criteria_ui import Ui_AddCriteriaDialog
from AddOrdinalOptionDialog import AddOrdinalOptionDialog

class AddCriteriaDialog(QDialog, Ui_AddCriteriaDialog):
    """Manages the add alternative dialog
    """
    def __init__(self, gui_manager, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.gui_manager = gui_manager
        self.isError = False    #Error flag for form processing
        self.errorMsg = ""
        self.ordinal_option_list = []
        
        #Connect slots to signals
        QObject.connect(self.help_define_criteria, QtCore.SIGNAL("help_button_clicked"), self.gui_manager.win.process_help_click)
        QObject.connect(self.add_criteria_box,QtCore.SIGNAL("accepted()"), self.process_accept)
        QObject.connect(self.add_criteria_box,QtCore.SIGNAL("rejected()"), self.close)
        QObject.connect(self.add_ordinal_option_button,QtCore.SIGNAL("clicked()"), self.start_add_ordinal_option)
        QObject.connect(self.remove_ordinal_option_button,QtCore.SIGNAL("clicked()"), self.handle_remove_ordinal_option)

    def load_crit_data(self, crit_data):        
        #Binary Example
        #[
        #   16, 
        #   u'Compliance with international regulations for species conservation', 
        #   u'Binary', 
        #   [['Compliant', 2], ['Not compliant', 1]], 
        #   u'B'
        #]
        #Ordinal Example
        #[
        #    22, 
        #    u'test', 
        #    u'Ordinal', 
        #    [('fewa', 1), ('blort', 2), ('foow', 3), ('eaw', 5), ('cracvk', 6)], 
        #    u'C'
        #]
        
        self.editing = True
        
        self.id = crit_data[0]
        name = crit_data[1]
        type = crit_data[2]
        options = crit_data[3]
        cb = crit_data[4]

        self.ordinal_option_list = options
        
        self.criteria_description_edit.setText(name)
        if cb == 'B':
            self.benefit_button.click()            
        elif cb == 'C':
            self.cost_button.click()        

        if type == 'Binary':  
            self.criteria_type_tab.setCurrentIndex(0)
            self.binary_yes_edit.setText(options[0][0])
            self.binary_no_edit.setText(options[1][0])         
        if type == 'Ordinal':
            self.criteria_type_tab.setCurrentIndex(1)
            if cb == 'C':
                options.reverse()
            self.ordinal_option_table.load(options)
                        
        elif type == 'Ratio':
            self.criteria_type_tab.setCurrentIndex(2)
            self.ratio_description_edit.setText(options)                        

    def process_accept(self):
        """Processes clicking of OK button in dialog
        
        Raises signal 'add_criteria_info_collected' along with structure containing all of the collected criteria data
        as (criteria description - str, criteria type - str, type specific data - str or list, cost/benefit - str)
        Calls for deletion of self when done s
        """
        self.errorMsg = ""
        criteria_info = None    #Holds all of the collected data including the type_info.  passed to observers
        type_info = None    #Holds collected data relative to the criteria type
        cost_benefit = None
        
        criteria_description = self.criteria_description_edit.text()
        if not criteria_description:
            self.isError = True
            self.errorMsg += "* Please enter a description of the criterion.\n"
        
        current_tab = self.criteria_type_tab.currentWidget()        
        if not current_tab:
            self.isError = True
            self.errorMsg += "* Please select a criteria type (ratio, binary, ordinal) and enter the appropriate information\n"
        
        current_tab_name = self.criteria_type_tab.tabText(self.criteria_type_tab.currentIndex())

        if self.benefit_button.isChecked():
            cost_benefit = "B"
        elif self.cost_button.isChecked():
            cost_benefit = "C"
        else:
            self.isError = True
            self.errorMsg += "* Please define criterion as a \"Benefit\" or \"Cost\"\n"

        if current_tab_name == "Ratio":
            ratio_description = self.ratio_description_edit.text()
            if not ratio_description:
                self.isError = True
                self.errorMsg += "* Please enter a description of the quantitative ratio value.\n"
            if not self.isError:
                type_info = unicode(ratio_description)
                
        elif current_tab_name == "Binary":
            binary_yes_description = self.binary_yes_edit.text()
            binary_no_description = self.binary_no_edit.text()
            if not binary_yes_description:
                self.isError = True
                self.errorMsg += "* Please enter a description for Option 1\n"
            if not binary_no_description:
                self.isError = True
                self.errorMsg += "* Please enter a description for Option 2\n"
            if not self.isError:
                if cost_benefit == 'B':
                    #If benefit then yes should be valued higher
                    type_info = [[unicode(binary_yes_description), 2],[unicode(binary_no_description), 1]]
                elif cost_benefit == 'C':
                    #If cost then no should be valued higher
                    type_info = [[unicode(binary_yes_description), 1],[unicode(binary_no_description), 2]]

            
                
        elif current_tab_name == "Ordinal":
            if len(self.ordinal_option_list) < 2:
                self.isError = True
                self.errorMsg += "* Your ordinal criterion must have at least two options\n"
            
            #if cost option then reverse option list to low-high
            if cost_benefit == 'C':
                self.ordinal_option_list.reverse()
                
            type_info = self.ordinal_option_list
            
        else:
            self.isError = True
            self.errorMsg += "Criteria add failed unexpectedly.\n"

        if self.isError:
            self.isError = False
            QMessageBox.critical(self,"Error adding criteria",self.errorMsg)
        else:
            criteria_info = [unicode(criteria_description), unicode(current_tab_name), type_info, cost_benefit]
            
            if self.editing:
                self.emit(SIGNAL("criteria_changed"), self.id, criteria_info)
            else:
                self.emit(SIGNAL("add_criteria_info_collected"), criteria_info)

    def start_add_ordinal_option(self):
        self.add_ordinal_option_dialog = AddOrdinalOptionDialog(self.gui_manager, self)
        self.connect(self.add_ordinal_option_dialog, SIGNAL("ordinal_option_info_collected"), self.finish_add_ordinal_option)
        self.add_ordinal_option_dialog.show()
    
    def finish_add_ordinal_option(self, option_info):
        self.errorMsg = ""
        (new_name, new_value) = option_info        
        for option in self.ordinal_option_list:
            (name, value) = option
            if new_value == value:
                self.isError = True
                self.errorMsg += "The option '"+unicode(name)+"' already has the rank of '"+unicode(value)+"'. Please choose another rank value."    
        
        if self.isError:
            self.isError = False
            QMessageBox.critical(self,"Error adding criteria",self.errorMsg)
        else:
            self.add_ordinal_option_dialog.hide()
            self.add_ordinal_option_dialog.deleteLater()
            
            num_options = len(self.ordinal_option_list)
            
            if num_options == 0:
                #New list
                self.ordinal_option_list.append(option_info)
            elif new_value < self.ordinal_option_list[num_options-1][1]:
                #Add to end
                self.ordinal_option_list.append(option_info)
            else:
                #Add to middle
                for i in range(num_options):
                    (name, value) = self.ordinal_option_list[i]
                    if new_value > value:
                        self.ordinal_option_list.insert(i, option_info)
                        break

            #for row in self.ordinal_option_list:
            #    print row
            self.ordinal_option_table.load(self.ordinal_option_list)

    def load_ordinal_option(self):
        pass

    def handle_remove_ordinal_option(self):
        if not self.ordinal_option_list:
            QMessageBox.critical(self,"Error Removing Option", "There are no options")
            return
        
        try:
            cur_row = self.ordinal_option_table.get_current_row()
        except DelphosError, e:
            QMessageBox.critical(self,"Error Removing Option", unicode(e))
        else:
            #Remove selected row
            self.ordinal_option_list.pop(cur_row)
            #Reload the table
            self.ordinal_option_table.load(self.ordinal_option_list)
    
    def process_reject(self):
        """Processes clicking of Cancel button in dialog
        """
        self.deleteLater()
        self.hide()             