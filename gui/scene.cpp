#include "scene.h"

#include <QGraphicsSceneMouseEvent>
#include <QDebug>
#include <QMimeData>
#include <QMouseEvent>

#include "value.h"
#include "datablock.h"

#include "map.h"
#include "reduce.h"
#include "sort.h"
#include "print.h"
#include "write.h"

#include "standardoperation.h"

Scene::Scene(QObject* parent)
  : QGraphicsScene(parent)
{
}

void Scene::dragEnterEvent(QGraphicsSceneDragDropEvent* event)
{
  //qDebug() << "DragNDrop Enter";
  //qDebug() << event->mimeData()->formats();
  if (event->mimeData()->hasFormat("application/x-chestnutpaletteitem")) {
    event->setProposedAction(Qt::CopyAction);
    event->accept();
    return;
  } else {
    event->ignore();
    QGraphicsScene::dragEnterEvent(event);
  }
}

void Scene::dragMoveEvent(QGraphicsSceneDragDropEvent* event)
{
  if (event->mimeData()->hasFormat("application/x-chestnutpaletteitem")) {
    event->setProposedAction(Qt::CopyAction);
    event->accept();
    return;
  } else {
    event->ignore();
    QGraphicsScene::dragMoveEvent(event);
  }
}

void Scene::dropEvent(QGraphicsSceneDragDropEvent* event)
{
  //qDebug() << "DragNDrop Drop";
  if (event->mimeData()->hasFormat("application/x-chestnutpaletteitem")) {
    QByteArray encodedData = event->mimeData()->data("application/x-chestnutpaletteitem");
    QDataStream stream(&encodedData, QIODevice::ReadOnly);
    QStringList newItems;

    while (!stream.atEnd()) {
        QString text;
        stream >> text;
        newItems << text;
    }
    QString droppedItem = newItems.first();
    
    
    QGraphicsItem *newItem = 0;
    
    // Data
    if (droppedItem == "Value") { newItem = new Value("value"); } 
    else if (droppedItem == "Data Block") { newItem = new DataBlock("datablock", "float", 10, 10); }
    
    //Functions
    else if (droppedItem == "Map") { newItem = new Map(); }
    else if (droppedItem == "Reduce") { newItem = new Reduce(); }
    else if (droppedItem == "Sort") { newItem = new Sort(); }
    else if (droppedItem == "Print") { newItem = new Print(); }
    else if (droppedItem == "Write") { newItem = new Write(); }
  
    else {
      qDebug() << "Unknown Item: " << droppedItem;
      return QGraphicsScene::dropEvent(event);
    }
    
    addItem(newItem);
    newItem->setPos(event->scenePos());
    qDebug() << event->scenePos();
    return;
  } else {
    QGraphicsScene::dropEvent(event);
  }
}


void Scene::keyPressEvent(QKeyEvent* event)
{
  if ((event->key() == Qt::Key_Delete) || (event->key() == Qt::Key_Backspace)) {
    event->accept();
    return;
  }
  QGraphicsScene::keyPressEvent(event);
}
void Scene::keyReleaseEvent(QKeyEvent* event)
{
  if ((event->key() == Qt::Key_Delete) || (event->key() == Qt::Key_Backspace)) {
    qDebug() << "#selected items:" << selectedItems().length();
    foreach(QGraphicsItem *item, selectedItems()) {
      qDebug() << "Removing" << item;
      delete item;
    }
    return;
  }
  QGraphicsScene::keyReleaseEvent(event);
}
