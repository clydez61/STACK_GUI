import sys, os, importlib,re
from PyQt5 import QtWidgets,QtGui,QtCore,uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#from Input_Dialog import Dialog
import resource
import json
from pylatexenc.latex2text import LatexNodes2Text
from nodeeditor.utils import *
from nodeeditor.node_editor_window import NodeEditorWindow
from stack_window import StackWindow
from stack_sub_window import *
from stack_drag_listbox import *
from stack_conf import *
from stack_conf_nodes import *
from stacked_input import *
import syntax_pars
list = []
WINDOW_SIZE = 0
selectedfonts = {}
selectedsizes = {}
syntax_dict = {}
float_dict = {}

#retrieve input info
varname_dict = {}
vartype_dict = {}
varans_dict = {}
varboxsize_dict = {}
lowestterm_dict = {}
hideanswer_dict = {}
allowempty_dict = {}
simplify_dict = {}

class MainWindow(QtWidgets.QMainWindow):
    
   
    
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__),"main_window_new.ui"),self)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        

        self.filename = None
        self.Dialog = Dialog()
        self.setTitle()
        self.actionSave.triggered.connect(lambda:self.onSave())
        self.actionOpen.triggered.connect(lambda:self.onOpen())
        self.actionSave_as.triggered.connect(lambda:self.onSaveAs())
        self.actionExport.triggered.connect(lambda:self.onExport())
        self.actionTemporary_save.triggered.connect(lambda:self.retrieveInput())
        #self.minimizeButton.clicked.connect(lambda: self.showMinimized()) 
        #self.closeButton.clicked.connect(lambda: self.close()) 
        #self.restoreButton.clicked.connect(lambda: self.restore_or_maximize_window())
       
        
        self.stackedWidget.setCurrentWidget(self.qedit_page)
        self.qvar_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.qvar_page))  
        self.qedit_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.qedit_page))        
        self.feedback_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.feedback_page))
        self.attributes_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.attributes_page))
        self.input_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.inputs_page))
        self.tree_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.tree_page))
        self.highlight = syntax_pars.PythonHighlighter(self.qvar_box.document())
        self.highlight2 = syntax_pars.PythonHighlighter(self.qtext_box.document())
        self.highlight3 = syntax_pars.PythonHighlighter(self.preview_box.document())
        self.tree_btn.clicked.connect(self.updateEditMenu)
        self.preview_btn.clicked.connect(self.preview)

        self.update_btn.clicked.connect(lambda: self.UpdateInput())
        self.savefile = None
        self.inputs = None
        self.NewFrame = None
        self.NewName = None
        self.NewSize = None
        self.NewAns = None
        self.NewType = None
        self.MoreButton = QPushButton
        self.dialog_syntax = None
        self.widgetname = None
        self.row = None
        self.column = None
        self.NewLayout = None
        self.NewGrid = None
        self.NewSyntax = None
        self.NewFloat = None
        self.Newlowest = None
        self.HideAnswer = None
        self.AllowEmpty = None
        self.Simplify = None
        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
        #setting ToolTip

        #html button for question text
        self.html_btn.setCheckable(True)
        self.html_btn.toggle()
        self.html_btn.clicked.connect(lambda:self.htmltoggle())
        

        #html button for general feedback
        self.html_btn2.setCheckable(True)
        self.html_btn2.toggle()
        self.html_btn2.clicked.connect(lambda:self.htmltoggle2())
        

        
        self.empty_icon = QIcon(".")

        self.nodeEditor = StackWindow()
        self.NodeEditorLayout.addWidget(self.nodeEditor)

        self.nodeEditor.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self.nodeEditor)
        self.windowMapper.mapped[QWidget].connect(self.nodeEditor.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.updateMenus()

        self.checkModified()
        self.menuEdit.aboutToShow.connect(self.updateEditMenu)
        def moveWindow(e):
            # Detect if the window is  normal size
            # ###############################################  
            if self.isMaximized() == False: #Not maximized
                # Move window only when window is normal size  
                # ###############################################
                #if left mouse button is clicked (Only accept left mouse button clicks)
                #FIXME: hasatrr() is a hacky fix, come up with solution to prevent click-drag of left-menu toggle button.
                if e.buttons() == Qt.LeftButton and hasattr(self, 'clickPosition'):  
                    #Move window 
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
        self.main_header.mouseMoveEvent = moveWindow    
        self.left_menu_toggle_btn.clicked.connect(lambda: self.slideLeftMenu())    

      

        #Setting up rich text bar
        
        
        #self.qtext_box.checkFontSignal.connect(self.checkFont)
        self.qtext_box.selectionChanged.connect(self.updatefont)
        self.qtext_box.selectionChanged.connect(self.updatesize)
        
        self.tfont_box.addItems(["Arial", "Times", "Courier", "Georgia", "Verdana",  "Trebuchet"])
        
        self.tfont_box.activated.connect(self.setFont)
    

        self.tsize_box.addItems(["6.75","7.5", "10", "12", "13.5", "18",  "24"])
        
        self.tsize_box.activated.connect(self.setFontSize)

        self.tbold_btn.setCheckable(True)
        self.tbold_btn.toggle()
        self.tbold_btn.clicked.connect(self.boldText)
        
        self.titalic_btn.setCheckable(True)
        self.titalic_btn.toggle()
        self.titalic_btn.clicked.connect(self.italicText)

        self.tunderline_btn.setCheckable(True)
        self.tunderline_btn.toggle()
        self.tunderline_btn.clicked.connect(self.underlineText)

        self.tleft_align_btn.clicked.connect(lambda : self.qtext_box.setAlignment(Qt.AlignLeft))
        self.tcenter_align_btn.clicked.connect(lambda : self.qtext_box.setAlignment(Qt.AlignCenter))
        self.tright_align_btn.clicked.connect(lambda : self.qtext_box.setAlignment(Qt.AlignRight))
  
        self.tordered_list_btn.clicked.connect(self.bulletList)
        self.ttext_color_btn.clicked.connect(self.setColor)
        self.tbcolor_btn.clicked.connect(self.setBackgroundColor)

        self.show()

    def setTitle(self):
        title = "STACK Question Editor - "
        title = title + (os.path.basename(self.filename) + '[*]' if self.filename is not None else "New Question[*]")

        self.setWindowTitle(title)

    def onOpen(self):
        try:
            fname, filter = QFileDialog.getOpenFileName(self, 'Open STACK question from file', os.path.dirname(__file__), 'STACK Question (*.json);;All files (*)')

            if fname != '' and os.path.isfile(fname):
                with open(fname, 'r') as file:
                    data = json.loads(file.read())
                    self.deserialize(data['nonNodeData'])
                    self.nodeEditor.deserialize(data['nodeData'])
                    self.filename = fname

                self.setTitle()
                self.setWindowModified(False)

        except Exception as e: dumpException(e)

    def onSave(self):
        data = self.combineNonNodeAndNodeData()
        if not self.isWindowModified():
            return
        else:
            if self.filename is not None:
                self.saveToFile(data, self.filename)
            else:
                self.onSaveAs()

    def onSaveAs(self):
        try:
            data = self.combineNonNodeAndNodeData()
            fname, filter = QFileDialog.getSaveFileName(self, 'Save STACK question to file', os.path.dirname(__file__), 'STACK Question (*.json);;All files (*)')
            if fname == '': return False

            self.setWindowTitle(fname)
            self.saveToFile(data, fname)
            self.filename = fname
            return True
        except Exception as e: dumpException(e)

    def saveToFile(self, data, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(data, indent=4))
            #print("saving to", filename, "was successful.")
            self.setWindowModified(False)

    def handleSelectionChanged(self):
        cursor = self.qtext_box.textCursor()
        return [cursor.selectionStart(), cursor.selectionEnd()];
        
    def setFont(self):
        font = self.tfont_box.currentText()
        self.qtext_box.setCurrentFont(QFont(font)) 
        selectedfonts[self.tfont_box.currentText()] = self.handleSelectionChanged()

        #just set for the following cursor locations, set font to ""



        
       
        # update the text-edit
    def updatefont(self):
        cursor2 = self.qtext_box.textCursor()
        #print(cursor2.selectionStart(),cursor2.selectionEnd())
        for textfont, cursorindex in selectedfonts.items():
            if cursor2.selectionStart() >= cursorindex[0] and cursor2.selectionEnd() <= cursorindex[1]:
                self.tfont_box.setCurrentText(textfont)
                break
            else:
                self.tfont_box.setCurrentText('Arial')
  

    def setFontSize(self):
        value = self.tsize_box.currentText()
        self.qtext_box.setFontPointSize(float(value))
        selectedsizes[self.tsize_box.currentText()] = self.handleSelectionChanged()
        print(selectedsizes)

    def updatesize(self):
        cursor2 = self.qtext_box.textCursor()
        for textsize, cursorindex in selectedsizes.items():
            if cursor2.selectionStart() >= cursorindex[0] and cursor2.selectionEnd() <= cursorindex[1]:
                self.tsize_box.setCurrentText(textsize)
                break
            else:
                self.tsize_box.setCurrentText('12')

    def setColor(self):         
        color = QColorDialog.getColor()
        self.qtext_box.setTextColor(color)

    def setBackgroundColor(self):     
        color = QColorDialog.getColor()
        self.qtext_box.setTextBackgroundColor(color)

    def boldText(self):
        if self.tbold_btn.isChecked():
            self.qtext_box.setFontWeight(QFont.Bold)
        else:
            self.qtext_box.setFontWeight(QFont.Normal)  

    def italicText(self):
        state = self.qtext_box.fontItalic()
        self.qtext_box.setFontItalic(not(state)) 

    def underlineText(self):
        state = self.qtext_box.fontUnderline()
        self.qtext_box.setFontUnderline(not(state))     

    def bulletList(self):
        cursor = self.qtext_box.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def preview(self):
        QApplication.processEvents()
        qtext_code = self.qtext_box.toPlainText()
        
        self.qtext_box.setAcceptRichText(True)
        self.preview_box.setAcceptRichText(True)
        #self.preview_box.setStyleSheet("color: rgb(85, 0, 255);")
        qtext_code = LatexNodes2Text().latex_to_text(qtext_code)
        stack_var = re.findall(r'\@[a-zA-z0-9]+\@', qtext_code)
        
        
        for elements in stack_var: 
            #font-size:8pt; to change            
            qtext_code = qtext_code.replace(elements,"{" + elements + "}")
        #self.preview_box.setStyleSheet("color: rgb(51, 51, 51);")
        
        
        self.preview_box.setText(qtext_code)

        
    def openDialog(self): #opens the dialog with the "more" button, openDialog() proceeds before set
        
        QApplication.processEvents()

        self.Dialog.input_save_btn.clicked.connect(lambda: self.set())

        syntax_content = {}
        try:
            for index, elem in enumerate(self.inputs):
                rows, lastrow = divmod(index, 4)


                #exec(f'self.connectClass.input_syntax{rows}_{lastrow}.setText({dialog_syntax})')
                #exec(f'history{index}.append("{dialog_syntax}")')
                

                #print(syntax_content)
                #syntax_content["syntax{}_{}".format(rows,lastrow)] = dialog_syntax
        except:
            pass
        
        self.Dialog.show()
    

    def expand(self,row,column):

        exec(f'global more_btn_checked; more_btn_checked = self.input_btn{str(row)}_{str(column)}.isChecked()')
        if more_btn_checked == True:
            exec(f'self.input_frame{str(row)}_{str(column)}.setMaximumSize(QSize(300, 330))')

            NewSyntax = f"input_syntax{str(row)}_{str(column)}"
            NewFloat = f"input_float{str(row)}_{str(column)}"
            NewSyntaxL = f"label_syntax{str(row)}_{str(column)}"
            NewFloatL = f"label_float{str(row)}_{str(column)}"
            NewlowestL = f"label_lowestTerms{str(row)}_{str(column)}"
            Newlowest =  f"input_lowestTerms{str(row)}_{str(column)}"
            
            
            HideAnswer = f"input_hideanswer{str(row)}_{str(column)}"
            AllowEmpty = f"input_allowempty{str(row)}_{str(column)}"
            Simplify = f"input_simplify{str(row)}_{str(column)}"
            NewextraOptions = f"label_extraOptions{str(row)}_{str(column)}"
            symbols = {"self": self,"QLabel":QLabel,"QTextEdit":QTextEdit,"Qt":Qt,"QComboBox":QComboBox}

            
            self.NewSyntax = NewSyntax
            self.NewFloat = NewFloat
            self.Newlowest = Newlowest
            self.HideAnswer = HideAnswer
            self.AllowEmpty = AllowEmpty
            self.Simplify = Simplify

            exec(f'self.input_btn{row}_{column}.setParent(None)')
            
            exec(f'self.label_syntax = QLabel(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewSyntaxL,self.label_syntax)
            self.label_syntax.setObjectName(u"label_size")
            self.label_syntax.setText("Syntax Hints")       
            self.label_syntax.setMaximumSize(QSize(16777215, 30))
            self.label_syntax.setAlignment(Qt.AlignVCenter)
            #self.formLayout_2.addRow(5, QFormLayout.LabelRole, self.label_syntax)

            exec(f'self.input_syntax = QTextEdit(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewSyntax,self.input_syntax)
            self.input_syntax.setObjectName(u'input_size')
            self.input_syntax.setMaximumSize(QSize(16777215, 100))
        
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow(self.label_syntax,self.input_syntax)',symbols)
            
            #self.formLayout_2.addRow(self.label_syntax,self.input_frame)
            #self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.input_syntax)

            #self.label_float = QLabel(self.input_frame)
            exec(f'self.label_float = QLabel(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewFloatL,self.label_float)
            self.label_float.setObjectName(u"input_float")
            self.label_float.setText("Forbid Float")

            

            #self.input_float = QComboBox(self.input_frame)
            exec(f'self.input_float = QComboBox(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewFloat,self.input_float)
            self.input_float.addItem(u"Yes")
            self.input_float.addItem(u"No")
            
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow(self.label_float,self.input_float)',symbols)
            
            #self.label_lowestTerms = QLabel(self.input_frame)
            exec(f'self.label_lowestTerms = QLabel(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewlowestL,self.label_lowestTerms)   
            self.label_lowestTerms.setText("Lowest Terms")
            

            #self.input_lowestTerms = QComboBox(self.input_frame)
            exec(f'self.input_lowestTerms = QComboBox(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,Newlowest,self.input_lowestTerms)
            self.input_lowestTerms.addItem(u"No")
            self.input_lowestTerms.addItem(u"Yes")

            
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow(self.label_lowestTerms,self.input_lowestTerms)',symbols)

            #self.label_extraOptions = QLabel(self.input_frame)
            exec(f'self.label_extraOptions = QLabel(self.input_frame{str(row)}_{str(column)})',symbols)
            setattr(self,NewextraOptions,self.label_extraOptions)
            
                
            self.label_extraOptions.setText("Extra Options")


            
            
            self.input_hideanswer = QCheckBox(self.input_frame)
            setattr(self,HideAnswer,self.input_hideanswer)
            self.input_hideanswer.setObjectName(u"input_hideanswer")
            self.input_hideanswer.setText("Hide Answer")


            self.input_allowempty = QCheckBox(self.input_frame)
            setattr(self,AllowEmpty,self.input_allowempty)
            self.input_allowempty.setObjectName(u"input_allowempty")
            self.input_allowempty.setText("Allow Empty")
            
            self.input_simplify = QCheckBox(self.input_frame)
            setattr(self,Simplify,self.input_simplify)
            self.input_simplify.setText("Simplify")
                       
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow(self.label_extraOptions,self.input_hideanswer)',symbols)
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow("",self.input_allowempty)',symbols)
            exec(f'self.input_layout{str(row)}_{str(column)}.addRow("",self.input_simplify)',symbols)

            exec(f'self.input_layout{str(row)}_{str(column)}.addRow(self.input_btn{row}_{column})',symbols)

            exec(f'self.input_btn{str(row)}_{str(column)}.setText("Save")',symbols)

            
            
            try:
                
                exec(f'self.input_syntax{str(row)}_{str(column)}.setText(syntax_dict["{str(row)}_{str(column)}"])')
                
                exec(f'self.input_float{str(row)}_{str(column)}.setCurrentText(float_dict["{str(row)}_{str(column)}"])')
                exec(f'self.input_lowestTerms{str(row)}_{str(column)}.setCurrentText(lowestterm_dict["{str(row)}_{str(column)}"])')
                if hideanswer_dict[f"{str(row)}_{str(column)}"] == True:
                    exec(f'self.input_hideanswer{str(row)}_{str(column)}.setChecked(True)')
                else:
                    exec(f'self.input_hideanswer{str(row)}_{str(column)}.setChecked(False)')
                if allowempty_dict[f"{str(row)}_{str(column)}"] == True:
                    exec(f'self.input_allowempty{str(row)}_{str(column)}.setChecked(True)')
                else:
                    exec(f'self.input_allowempty{str(row)}_{str(column)}.setChecked(False)')
                if simplify_dict[f"{str(row)}_{str(column)}"] == True:
                    exec(f'self.input_simplify{str(row)}_{str(column)}.setChecked(True)')
                else:
                    exec(f'self.input_simplify{str(row)}_{str(column)}.setChecked(False)')
            except:
                pass
        else:
            
            #save the input fields before removing
            self.normal_dict_save(row,column)
            self.expand_dict_save(row,column)
            
            exec(f'self.input_btn{str(row)}_{str(column)}.setText("More..")')

            exec(f'self.label_syntax{str(row)}_{str(column)}.setParent(None)')
            exec(f'self.input_syntax{str(row)}_{str(column)}.setParent(None)')

            exec(f'self.label_float{str(row)}_{str(column)}.setParent(None)')
            exec(f'self.input_float{str(row)}_{str(column)}.setParent(None)')

            exec(f"self.label_lowestTerms{str(row)}_{str(column)}.setParent(None)")
            exec(f"self.input_lowestTerms{str(row)}_{str(column)}.setParent(None)")

            exec(f"self.input_hideanswer{str(row)}_{str(column)}.setParent(None)")
            exec(f"self.input_allowempty{str(row)}_{str(column)}.setParent(None)")
            exec(f"self.input_simplify{str(row)}_{str(column)}.setParent(None)")
            exec(f"self.label_extraOptions{str(row)}_{str(column)}.setParent(None)")
            
            
    def expand_dict_save(self,row,column):
        QApplication.processEvents()
        widgetname = f'{row}_{column}'
        exec(f'global syntax; syntax = self.input_syntax{str(row)}_{str(column)}.toPlainText()')                               
        syntax_dict.update({"{}".format(widgetname):syntax})

        exec(f'global allow_float; allow_float = self.input_float{str(row)}_{str(column)}.currentText()')
        float_dict.update({"{}".format(widgetname):allow_float})
        
        exec(f'global lowest_terms; lowest_terms = self.input_lowestTerms{str(row)}_{str(column)}.currentText()')
        lowestterm_dict.update({"{}".format(widgetname):lowest_terms})

        exec(f"global hide_answer; hide_answer = self.input_hideanswer{str(row)}_{str(column)}.isChecked()")
        hideanswer_dict.update({"{}".format(widgetname):hide_answer})

        exec(f"global allow_empty; allow_empty = self.input_allowempty{str(row)}_{str(column)}.isChecked()")
        allowempty_dict.update({"{}".format(widgetname):allow_empty})

        exec(f"global simplify; simplify = self.input_simplify{str(row)}_{str(column)}.isChecked()")
        simplify_dict.update({"{}".format(widgetname):simplify})                  
            
        


        self.widgetname = widgetname

    def normal_dict_save(self,row,column):
        QApplication.processEvents()
        widgetname = f'{row}_{column}'

        exec(f"global varname; varname = self.input_name{str(row)}_{str(column)}.toPlainText()")
        varname_dict.update({"{}".format(widgetname):varname})


        exec(f"global vartype; vartype = self.input_type{str(row)}_{str(column)}.currentText()")
        vartype_dict.update({"{}".format(widgetname):vartype})

        exec(f"global varboxsize; varboxsize = self.input_size{str(row)}_{str(column)}.toPlainText()")
        varboxsize_dict.update({"{}".format(widgetname):varboxsize})

        exec(f"global varans; varans = self.input_ans{str(row)}_{str(column)}.toPlainText()")
        varans_dict.update({"{}".format(widgetname):varans})
        
        
        
        

    def retrieveInput(self):
        #copy this line to your save function,before you call dicts
        for i in range(self.row+1):
            for j in range(self.column+1):
                QApplication.processEvents()
                self.normal_dict_save(i,j)
                try:
                    self.expand_dict_save(i,j)
                except:
                    pass
        
        # I made dictionaries for each term it will automatically update as user fill in,
        # you just need to call them, here below is the list of dicts, the key name is in the format of "row"_"column"
        # this function "retreieveInput" currently binded to the "Help -> Temporary save" on the menubar, feel free to remove
        # Also now you can type whatever input name you want inside [[]], changed it 

        print(syntax_dict,float_dict,lowestterm_dict, hideanswer_dict ,allowempty_dict ,simplify_dict )
        print(varname_dict,vartype_dict,varans_dict,varboxsize_dict)
        
        print('input retrieved')
        

    def UpdateInput(self):
        QApplication.processEvents()
        
        current_text = self.qtext_box.toPlainText()
        inputs = re.findall(r'\[\[[\w-]+\]\] ', current_text) 
        symbols = {"self": self}
        try:
            exec(f'self.input_frame.setParent(None)')
        except:
            pass
        for index, elem in enumerate(inputs):
            rows, lastrow = divmod(index, 4)                            
            self.addInput(rows,lastrow)
            
            exec(f'self.input_btn{rows}_{lastrow}.clicked.connect(lambda: self.expand({rows},{lastrow}))',symbols) 
            widgetname2 = f'{rows}_{lastrow}'              
            
            self.input_name.setText(elem[2:-2])            
            self.input_size.setText("5")
            
            #self.input_size.toPlainText() for Box Size
            #unicode(self.input_type.currentText()) for Input Type
            
        
        #To store or save user input fo "input" section:
        #self.input_name.toPlainText() for Name
        #self.input_ans.toPlainText() for Model answer
        #self.input_size.toPlainText() for Box Size
        #unicode(self.input_type.currentText()) for Input Type
        self.inputs = inputs    

            #self.addInput()
            #i+=1

    def addInput(self,row,column): #triggers by clicking update 
        
        NewFrame = f"input_frame{str(row)}_{str(column)}"
        NewName = f"input_name{str(row)}_{str(column)}"
        NewLayout = f"input_layout{str(row)}_{str(column)}"
        
        
        NewAns = f"input_ans{str(row)}_{str(column)}"
        NewSize = f"input_size{str(row)}_{str(column)}"
        NewType = f"input_type{str(row)}_{str(column)}"
        MoreButton = f"input_btn{str(row)}_{str(column)}"
        self.NewFrame = NewFrame
        self.NewName = NewName
        self.NewSize = NewSize
        self.NewAns = NewAns
        self.NewType = NewType
        self.MoreButton = MoreButton
        self.NewLayout = NewLayout
        self.input_frame = QFrame(self.ScrollPage)
        setattr(self, NewFrame, self.input_frame)

        self.input_frame.setMinimumSize(QSize(100, 100))
        self.input_frame.setMaximumSize(QSize(300, 300))
        
        self.input_frame.setFrameShape(QFrame.StyledPanel)
        self.input_frame.setFrameShadow(QFrame.Raised)
        self.input_frame.setObjectName(u"QFrame")
        self.input_frame.setStyleSheet(u"font: 5pt \"MS Sans Serif\";color: rgb(255, 255, 222);background-color: rgb(51, 51, 51);border-color: rgb(255, 255, 0);")
        self.ScrollPage.setStyleSheet(u"#QFrame{border:2px solid rgb(255,0,0)}")
        self.formLayout_2 = QFormLayout(self.input_frame)
        self.formLayout_2.setObjectName(u"formLayout_2")

        setattr(self, NewLayout, self.formLayout_2)
        self.label_name = QLabel(self.input_frame)
        self.label_name.setObjectName(u"label_name")
        self.label_name.setText("Name")
        self.label_name.setToolTip("The Name of the Input, can be used in the potential tree section\n Edit through the Question Text Section")
        self.label_name.setAlignment(Qt.AlignCenter)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_name)

        self.input_name = QTextEdit(self.input_frame)
        self.input_name.setObjectName(u'input_name')
        self.input_name.setMaximumSize(QSize(16777215, 30))

        
        
       
        setattr(self,NewName,self.input_name)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.input_name)

        self.label_type = QLabel(self.input_frame)
        self.label_type.setObjectName(u"label_type")
        self.label_type.setText("Type")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_type)

        self.input_type = QComboBox(self.input_frame)
        setattr(self,NewType,self.input_type)
        self.input_type.addItem(u"Algebraic Input")
        self.input_type.addItem(u"Checkbox")
        self.input_type.addItem(u"Drop down List")
        self.input_type.addItem(u"Equivalence reasoning")
        self.input_type.addItem(u"Matrix")
        self.input_type.addItem(u"Notes")
        self.input_type.addItem(u"Numerical")
        self.input_type.addItem(u"Radio")
        self.input_type.addItem(u"Single Character")
        self.input_type.addItem(u"String")
        self.input_type.addItem(u"Text Area")
        self.input_type.addItem(u"True/False")
        self.input_type.addItem(u"Units")
        self.input_type.setObjectName(NewType)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.input_type)

        self.label_ans = QLabel(self.input_frame)
        self.label_ans.setObjectName(u"label_ans")
        self.label_ans.setText("Answer")
        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_ans)

        self.input_ans = QTextEdit(self.input_frame)
        self.input_ans.setObjectName(NewAns)
        self.input_ans.setMaximumSize(QSize(16777215, 30))
        setattr(self,NewAns,self.input_ans)
        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.input_ans)

        self.label_size = QLabel(self.input_frame)
        self.label_size.setObjectName(u"label_size")
        self.label_size.setText("Box Size")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_size)

        self.input_size = QTextEdit(self.input_frame)
        setattr(self,NewSize,self.input_size)
        self.input_size.setObjectName(u'input_size')
        self.input_size.setMaximumSize(QSize(16777215, 30))
        
        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.input_size)

        self.more_btn = QPushButton(self.NewFrame)
        setattr(self,MoreButton,self.more_btn)
        self.more_btn.setObjectName(u"more_btn")
        self.more_btn.setText(u"More..")        
        self.more_btn.setCheckable(True)
        


        symbols = {"self": self}
        
        

        #self.more_btn.clicked.connect(lambda: self.expand(row,column))
        
        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.more_btn)

        
        
        self.gridLayout_2.addWidget(self.input_frame, row, column, 1, 1)
        self.row = row
        self.column = column

    def checkModified(self):
        #set up checks to see if window is modified
        self.qvar_box.document().modificationChanged.connect(self.setWindowModified)
        self.qtext_box.document().modificationChanged.connect(self.setWindowModified)
        self.gfeedback_box.document().modificationChanged.connect(self.setWindowModified)
        self.sfeedback_box.document().modificationChanged.connect(self.setWindowModified)
        self.grade_box.document().modificationChanged.connect(self.setWindowModified)
        
        self.ID_box.document().modificationChanged.connect(self.setWindowModified)
        self.qnote_box.document().modificationChanged.connect(self.setWindowModified)
        self.tag_box.document().modificationChanged.connect(self.setWindowModified)

        self.nodeEditor.nodeEditorModified.connect(lambda:self.setWindowModified(True))

    def createActions(self):
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)

    def createMenus(self):
        self.menuEdit.clear()

        self.menuEdit.addAction(self.actNew)
        self.menuEdit.addAction(self.nodeEditor.actUndo)
        self.menuEdit.addAction(self.nodeEditor.actRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.nodeEditor.actCut)
        self.menuEdit.addAction(self.nodeEditor.actCopy)
        self.menuEdit.addAction(self.nodeEditor.actPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.nodeEditor.actDelete)
        self.menuEdit.addSeparator()
        self.nodesToolbar = self.menuEdit.addAction("Nodes Toolbar")
        self.nodesToolbar.setCheckable(True)
        self.nodesToolbar.triggered.connect(self.nodeEditor.onWindowNodesToolbar)
        self.propertiesToolbar = self.menuEdit.addAction("Properties Toolbar")
        self.propertiesToolbar.setCheckable(True)
        self.propertiesToolbar.triggered.connect(self.nodeEditor.onWindowPropertiesToolbar)
        self.menuEdit.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        # May contain other menu items
        self.updateEditMenu()

    def updateEditMenu(self):
        active = self.nodeEditor.getCurrentNodeEditorWidget() 
        self.actNew.setEnabled(self.nodeEditor.isVisible())
        self.nodesToolbar.setEnabled(self.nodeEditor.isVisible())
        self.nodesToolbar.setChecked(self.nodeEditor.nodesDock.isVisible())	
        self.propertiesToolbar.setEnabled(self.nodeEditor.isVisible())
        self.propertiesToolbar.setChecked(self.nodeEditor.propertiesDock.isVisible())

        hasMdiChild = (active is not None)
        self.nodeEditor.actPaste.setEnabled(hasMdiChild)
        self.nodeEditor.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
        self.nodeEditor.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
        self.nodeEditor.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

        self.nodeEditor.actUndo.setEnabled(hasMdiChild and active.canUndo())
        self.nodeEditor.actRedo.setEnabled(hasMdiChild and active.canRedo())

    def onFileNew(self):
        try:
            subwnd = self.nodeEditor.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e: dumpException(e)

    def htmltoggle(self):
        textformat = self.qtext_box.toPlainText()        
        if self.html_btn.isChecked():
            htmlformat = repr(self.qtext_box.toPlainText())
            
            htmlformat = r'<p>' + textformat.replace("\n", "<br>") + r'</p>'
            print(htmlformat)
            
            self.qtext_box.setPlainText(htmlformat)

            self.html_btn.setStyleSheet("background-color : lightblue")
  
        else:
            
            self.qtext_box.setHtml(textformat)


    def htmltoggle2(self):
        textformat = self.gfeedback_box.toPlainText()        
        if self.html_btn2.isChecked():
            htmlformat = repr(self.gfeedback_box.toPlainText())
            
            htmlformat = r'<p>' + textformat.replace("\n", "<br>") + r'</p>'
            
            
            self.gfeedback_box.setPlainText(htmlformat)

            self.html_btn2.setStyleSheet("background-color : lightblue")
  
        else:
            
            self.gfeedback_box.setHtml(textformat)    

    def onExport(self):
        print(self.isWindowModified())

    def open(self):
        fname = QFileDialog.getOpenFileName(self,'Open File','STACK_QT5','(*.py)') #(*.py *.xml *.txt)
        path = fname[0]
        split_string = path.rsplit("/",1)
        imp_path = split_string[0] 
        imp_path += '/'
        name = split_string[-1].split(".")
        imp_name = name[0]
        
        if imp_name and imp_path != '':
            sys.path.insert(0, imp_path)
            
            mod = importlib.import_module(imp_name)

        #make the variable global
            print(f"path:{imp_path},name = {imp_name}")

            #self.qvar_box.clear()
            self.qvar_box.setPlainText(mod.question.get('questionvariables')[1:-1])     
            self.qtext_box.setPlainText(mod.question.get('questiontext')[1:-1])           
            self.gfeedback_box.setPlainText(mod.question.get('generalfeedback')[1:-1])               
            self.sfeedback_box.insertPlainText(mod.question.get('specificfeedback')[1:-1])               
            self.grade_box.setPlainText(mod.question.get('defaultgrade'))     
            #self.penalty_box.setPlainText(mod.question.get('penalty'))
            self.ID_box.setPlainText(mod.question.get('idnumber'))       
            self.qnote_box.setPlainText(mod.question.get('questionnote')[1:-1])  

            key = mod.question.get('tags')
            result = ''
            for elements in key['tag']: 
                result += str(elements) + "\n" 
            self.tag_box.setText(result)
            print(f"path is {imp_path}, name is {imp_name}")

    def save_as(self):
        if not self.isWindowModified():
            return
        savefile, _ = QFileDialog.getSaveFileName(self,'Save File','STACK_QT5','(*.py)')
        if savefile:
            pyout = open(savefile,'w')
            pyout.write("question = {")

            #writing question text
            pyout.write('   "questiontext":"""\n')
            pyout.write(str(self.qtext_box.toPlainText()))
            pyout.write('\n""",\n')

            #writing question variables
            pyout.write('   "questionvariables":"""\n')
            pyout.write(str(self.qvar_box.toPlainText()))
            pyout.write('\n""",\n')

            #writing general feedback
            pyout.write('   "generalfeedback":"""\n')
            pyout.write(str(self.gfeedback_box.toPlainText()))
            pyout.write('\n""",\n')
            
            #writing default grade
            pyout.write('   "defaultgrade":')
            pyout.write('"' + str(self.grade_box.toPlainText()) + '",\n')

            #writing question note
            pyout.write('   "questionnote":"""\n')
            pyout.write(str(self.qnote_box.toPlainText()))
            pyout.write('\n""",\n')

            # writing tags
            pyout.write('   "tags":{\n')
            pyout.write('       "tag": [\n')                
            pyout.write(str(self.tag_box.toPlainText()) + '\n')
            pyout.write('       ]\n')
            pyout.write('   },\n')

            #writing ID
            pyout.write('   "idnumber":')
            pyout.write('"' + str(self.ID_box.toPlainText()) + '",\n')

            #penalty
      
          
            pyout.write("\n}")
                                    
            self.savefile = savefile
            self.setWindowTitle(str(os.path.basename(savefile)))

    def save(self):
        # if savefile[0] already exists, then save, if savefile[0] does not, then open save_file    
        if not self.isWindowModified():
            return

        if not self.savefile:
            self.save_as()
        else:
            pyout = open(self.savefile,'w')
            pyout.write("question = {")

            #writing question text
            pyout.write('   "questiontext":"""\n')
            pyout.write(str(self.qtext_box.toPlainText()))
            pyout.write('\n""",\n')

            #writing question variables
            pyout.write('   "questionvariables":"""\n')
            pyout.write(str(self.qvar_box.toPlainText()))
            pyout.write('\n""",\n')

            #writing general feedback
            pyout.write('   "generalfeedback":"""\n')
            pyout.write(str(self.gfeedback_box.toPlainText()))
            pyout.write('\n""",\n')
            
            #writing default grade
            pyout.write('   "defaultgrade":')
            pyout.write('"' + str(self.grade_box.toPlainText()) + '",\n')

            #writing question note
            pyout.write('   "questionnote":"""\n')
            pyout.write(str(self.qnote_box.toPlainText()))
            pyout.write('\n""",\n')

            # writing tags
            pyout.write('   "tags":{\n')
            pyout.write('       "tag": [\n')                
            pyout.write(str(self.tag_box.toPlainText()) + '\n')
            pyout.write('       ]\n')
            pyout.write('   },\n')

            #writing ID
            pyout.write('   "idnumber":')
            pyout.write('"' + str(self.ID_box.toPlainText()) + '",\n')

            #penalty

            pyout.write("\n}")
   
    def restore_or_maximize_window(self):
        # Global windows state
        global WINDOW_SIZE #The default value is zero to show that the size is not maximized
        win_status = WINDOW_SIZE

        if win_status == 0:
        	# If the window is not maximized
        	WINDOW_SIZE = 1 #Update value to show that the window has been maxmized
        	self.showMaximized()

        	# Update button icon  when window is maximized
        	self.restoreButton.setIcon(QtGui.QIcon(u":/icons/icons/cil-window-restore.png"))#Show minized icon
        else:
        	# If the window is on its default size
            WINDOW_SIZE = 0 #Update value to show that the window has been minimized/set to normal size (which is 800 by 400)
            self.showNormal()

            # Update button icon when window is minimized
            self.restoreButton.setIcon(QtGui.QIcon(u":/icons/icons/cil-window-maximize.png"))#Show maximize icon

    def mousePressEvent(self, event):
       
        # Get the current position of the mouse
        self.clickPosition = event.globalPos()
    
    def slideLeftMenu(self):
        # Get current left menu width
        width = self.left_side_menu.width()

        # If minimized
        if width == 50:
            # Expand menu
            newWidth = 150
        # If maximized
        else:
            # Restore menu
            newWidth = 50

        # Animate the transition
        self.animation = QPropertyAnimation(self.left_side_menu, b"minimumWidth")#Animate minimumWidht
        self.animation.setDuration(250)
        self.animation.setStartValue(width)#Start value is the current menu width
        self.animation.setEndValue(newWidth)#end value is the new menu width
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


    def serialize(self):
        qvar = self.qvar_box.toPlainText()
        qtext = self.qtext_box.toPlainText()
        generalfeedback = self.gfeedback_box.toPlainText()
        specificfeedback = self.sfeedback_box.toPlainText()
        grade = self.grade_box.toPlainText()
        mainid = self.ID_box.toPlainText()
        qnote = self.qnote_box.toPlainText()
        tags = self.tag_box.toPlainText()
        return OrderedDict([
            ('questionVar', qvar),
            ('questionText', qtext),
            ('generalFeedback', generalfeedback),
            ('specificFeedback', specificfeedback),
            ('grade', grade),
            ('mainID', mainid),
            ('questionNote', qnote),
            ('tags', tags),
        ])
    
    def deserialize(self, data, hashmap=[]):
        try:
            self.qvar_box.setPlainText(data['questionVar'])
            self.qtext_box.setPlainText(data['questionText'])
            self.gfeedback_box.setPlainText(data['generalFeedback'])
            self.sfeedback_box.setPlainText(data['specificFeedback'])
            self.grade_box.setPlainText(data['grade'])
            self.ID_box.setPlainText(data['mainID'])
            self.qnote_box.setPlainText(data['questionNote'])
            self.tag_box.setPlainText(data['tags'])
        except Exception as e: dumpException(e)

    def combineNonNodeAndNodeData(self):
        nonNodeData = self.serialize()
        nodeData = self.nodeEditor.serialize()
        data = OrderedDict([
            ('nonNodeData', nonNodeData),
            ('nodeData', nodeData), 
        ])
        return data

class Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__),"InputDialog.ui"),self)
        self.NewFrameD = None
        self.NewSyntax = None
        self.NewFloat = None
        self.NewButton2 = None
        
    def saving(self):
        QApplication.processEvents()
        
    def new_dialog(self,row,column):
        NewFrameD = f"input_frameD{str(row)}_{str(column)}"
        NewSyntax = f"input_syntax{str(row)}_{str(column)}"
        NewButton2 = f"input_save_btn{str(row)}_{str(column)}"
        print(NewSyntax)
        NewFloat  = f"input_float{str(row)}_{str(column)}"
        self.NewFrameD = NewFrameD
        self.NewSyntax = NewSyntax
        self.NewFloat = NewFloat
        self.NewButton2 = NewButton2
        setattr(self, NewFrameD, self.input_frameD)
        setattr(self, NewSyntax, self.input_syntax)
        setattr(self, NewFloat, self.input_float)
        setattr(self, NewButton2, self.input_save_btn)
        

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv) 
  
    window = MainWindow() # Create an instance of our class
    
    window.show()
    sys.exit(app.exec_())   