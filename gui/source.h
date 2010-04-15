#ifndef CHESTNUT_SOURCE_H
#define CHESTNUT_SOURCE_H

#include <QGraphicsObject>

#include "data.h"

class Connection;
class Object;
class Sink;

class Source : public QGraphicsObject {
  public:
    Source(Data::Type type, Object *parent);
    Data::Type dataType() const;
    
    Connection* connectToSink(Sink *sink);
    
    void addConnection(Connection *connection);
    void removeConnection(Connection *connection);
    void removeAllConnections();
    
    QPointF connectedCenter() const;
    
    virtual void mousePressEvent(QGraphicsSceneMouseEvent* event);
    virtual void mouseMoveEvent(QGraphicsSceneMouseEvent* event);
    virtual void mouseReleaseEvent(QGraphicsSceneMouseEvent* event);
    
    virtual QRectF boundingRect() const;
    virtual void paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget = 0);
  private:
    Data::Type m_dataType;
    QList<Connection*> m_connections;
    qreal m_width;
    qreal m_height;
    Connection* m_activeConnection;
    
};

#endif //CHESTNUT_SOURCE_H