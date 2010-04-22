#include "connection.h"

#include "source.h"
#include "sink.h"
#include "drawingutils.h"
#include "sizes.h"

#include <QPainter>
#include <QDebug>

using namespace Chestnut;


Connection::Connection(Source* source, Sink* sink)
  : QGraphicsItem(source)
{
  m_source = source;
  m_sink = sink;
  source->addConnection(this);
  sink->setConnection(this);
}

Connection::Connection(Source* source) 
  : QGraphicsItem(source)
{
  m_source = source;
  source->addConnection(this);
  m_sink = 0;
  m_partialEndpoint = source->connectedCenter();  
}

Connection::~Connection()
{
  if (m_source) {
    m_source->removeConnection(this);
  }
  if (m_sink) {
    m_sink->setConnection(0);
  }
}

void Connection::updateConnection()
{
  prepareGeometryChange();
  update();
}

bool Connection::isPartial() const
{
  return (m_sink == 0);
}
void Connection::setSink(Sink* sink)
{
  prepareGeometryChange();
  m_sink = sink;
  if (sink) {
    sink->setConnection(this);
  }
}
void Connection::setEndpoint(const QPointF& scenePoint)
{
  prepareGeometryChange();
  m_partialEndpoint = mapFromScene(scenePoint);
}
QPointF Connection::endpoint() const
{
  return isPartial() ? m_partialEndpoint : mapFromItem(sink(), sink()->connectedCenter());
}
QRectF Connection::boundingRect() const
{
  return path().boundingRect().united(endShape().boundingRect()).adjusted(-2, -2, 2, 2); // margin is 2
}

Source* Connection::source() const
{
  return m_source;
}
Sink* Connection::sink() const
{
  return m_sink;
}

QPainterPath Connection::path() const
{
  //qDebug() << "Path of Connection";
  QPointF start = mapFromItem(source(), source()->connectedCenter());
  QPointF end = endpoint();
  
  QLineF line = QLineF(start, end);
  QPointF midpoint = line.pointAt(0.5);
  
  QLineF firstLine = QLineF(start, midpoint);
  QLineF secondLine = QLineF(midpoint, end);
  
  QPointF controlPoint1 = firstLine.pointAt(0.5);
  QPointF controlPoint2 = secondLine.pointAt(0.5);
  
  controlPoint1 += QPointF(0, 10);
  controlPoint2 -= QPointF(0, 10);
  
  QPainterPath path;
  path.moveTo(start);
  path.quadTo(controlPoint1, midpoint);
  path.quadTo(controlPoint2, end);

  return path;
}

QPainterPath Connection::endShape() const
{
  QPainterPath p;
  switch (source()->dataType()) {
    case Data::DataBlock:
      p.addEllipse(endpoint(), Size::inputRadius, Size::inputRadius);
      return p;
      break;
    case Data::Value:
      return triangle(endpoint(), Size::inputHeight, Size::inputWidth);
      break;
  }
}

void Connection::paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget)
{  
  //qDebug() << "Painting Connection";
  QPen p;
  p.setWidth(2);
  painter->setPen(p);
  painter->drawPath(path());
  
  p.setWidth(1);
  painter->setPen(p);
  painter->drawPath(endShape());
}
