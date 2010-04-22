#include "sink.h"

#include "sizes.h"
#include "drawingutils.h"
#include "connection.h"
#include "source.h"
#include "object.h"

#include <QPainter>
#include <QDebug>

using namespace Chestnut;

Sink::Sink(Data::Types allowedTypes, Object* parent)
  : QGraphicsObject(parent)
{
  m_allowedTypes = allowedTypes;
  m_connection = 0;
  m_internalMargin = 2;
  m_parent = parent;
  connect(parent, SIGNAL(xChanged()), this, SLOT(moved()));
  connect(parent, SIGNAL(yChanged()), this, SLOT(moved()));
}
Data::Types Sink::allowedTypes() const
{
  return m_allowedTypes;
}

int Sink::type() const
{
  return Type;
}

Object* Sink::parentObject() const
{
  return m_parent;
}

Source* Sink::connectedSource() const
{
  if (m_connection) {
    return m_connection->source();
  }
}

void Sink::setConnection(Connection* connection)
{
  if (!connection) {
    m_connection = connection;
    return;
  }
  
  Data::Type type = connection->source()->dataType();
  Q_ASSERT(allowedTypes().contains(type));
  
  m_connection = connection;
  m_connectionType = type;
}

Connection* Sink::connection() const
{
  return m_connection;
}

QPointF Sink::connectedCenter()
{
  if (!m_connection) {
    return QPointF();
  }
  
  int location = m_allowedTypes.indexOf(m_connectionType);
  QPointF center(inputWidth/2, inputHeight/2);
  center += QPointF(location*(m_internalMargin + inputWidth), 0);
  return center;
}

QRectF Sink::rect() const {
  qreal totalWidth = 0;
  foreach(Data::Type type, m_allowedTypes) {
    totalWidth += inputWidth;
  }
  totalWidth += m_internalMargin*m_allowedTypes.length();

  QPointF topLeft = QPointF(0, 0);
  QPointF bottomRight = QPointF(totalWidth, inputHeight);
  return QRectF(topLeft, bottomRight);
}

QRectF Sink::boundingRect() const
{
  return rect().adjusted(-1, -1, 1, 1);
}
void Sink::paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget)
{
  QPen p(Qt::black, 1, Qt::DotLine);
  painter->setPen(p);
  
  QPointF topLeft = QPointF(0, 0);
  
  foreach(Data::Type type, m_allowedTypes) {
    QPointF center = topLeft + QPointF(inputWidth/2, inputHeight/2);
    switch (type) {
      case Data::Value:
        painter->drawPath(triangle(center, inputWidth, inputHeight));
        break;
    
      case Data::DataBlock:
        painter->drawEllipse(center, inputWidth/2, inputHeight/2);
        break;
        
      default:
        qDebug() << "Unhandled datatype" << type;
        break;
    }
  topLeft = QPointF(topLeft.x() + inputWidth + m_internalMargin, topLeft.y());
  }
}

void Sink::moved() {
  //qDebug() << "sink moved";
  if (m_connection) {
    m_connection->updateConnection();
  }
}

