#include "value.h"

#include "sizes.h"
#include "drawingutils.h"
#include "source.h"

#include <QPainter>
#include <QApplication>
#include <QDebug>

using namespace Chestnut;

Value::Value( const QString& name, const QString& datatype)
  : Data(name, Data::Value, datatype)
{
  m_name = name;
  
  Source *outputValue = new Source(Data::Value, this);
  m_sources.append(outputValue);
  
  qreal xpos = Size::valueWidth/2 - Size::outputWidth/2;
  outputValue->setPos(QPointF(xpos, Size::valueHeight));
}

Value::~Value()
{

}

ProgramStrings Value::flatten() const
{
  QString valueInChestnut = "scalar";
  QString declaration = datatype() + " " + name() + " " + valueInChestnut;
  qDebug() << "flatten called on value: " << declaration;
  ProgramStrings ps;
  ps.first.append(declaration);
  return ProgramStrings();
}

QRectF Value::boundingRect() const
{
  QPointF margin(1, 1);
  return QRectF(QPointF(0, 0) - margin,
                QPointF(Size::valueWidth, Size::valueHeight) + margin);
}

void Value::paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget)
{
  
  QPointF center = QPointF(Size::valueWidth/2, Size::valueHeight/2);
  painter->drawPath(triangle(center, Size::valueWidth, Size::valueHeight));
  
  // Layout and draw text
  qreal xpos = Size::valueWidth/2;
  qreal ypos = Size::valueHeight;
  
  xpos -= 0.5*QApplication::fontMetrics().width(m_name);
  ypos -= 5;
  painter->drawText(xpos, ypos, m_name);
}
