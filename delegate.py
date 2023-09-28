from PyQt5.QtWidgets import  QApplication, QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt5.QtCore import  QSize
from PyQt5 import QtGui

class MultiLineDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = (
            QApplication.style() if options.widget is None 
            else options.widget.style()
        )

        doc = QtGui.QTextDocument()
        doc.setPlainText(options.text)
        doc.setTextWidth(options.rect.width())
        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        # Highlighting selection if item is selected
        # without this, text won't appear selected
        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(
                QtGui.QPalette.Text,
                option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText),
            )
        else:
            ctx.palette.setColor(
                QtGui.QPalette.Text,
                option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Text),
            )

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options, None)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        doc = QtGui.QTextDocument()
        doc.setPlainText(options.text)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())

