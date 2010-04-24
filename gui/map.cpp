#include "map.h"
#include "source.h"
#include "sink.h"
#include "standardoperation.h"
#include "data.h"

#include <QDebug>

Map::Map(QGraphicsObject* parent)
  : Function("map", parent)
{
  Data::Formats in1;
  in1 << Data::DataBlock;
 
  Data::Formats in2;
  in2 << Data::DataBlock;
  in2 << Data::Value;
  
  Sink *input1 = new Sink(in1, this);
  addSink(input1);
  Sink *input2 = new Sink(in2, this);
  addSink(input2);

  Source *output1 = new Source(Data::DataBlock, this);
  addSource(output1);
  
  Operation *op = new StandardOperation(StandardOperation::Add, this); // TODO allow op to be set
  setHasOperation(true);
  setOperation(op);
}

int Map::type() const
{
  return Type;
}

ProgramStrings Map::flatten() const
{
  if (isVisited()){
    return ProgramStrings();
  }
  
  setVisited(true);
 
  ProgramStrings prog;
  
  foreach(Sink *sink, sinks()){
    Data* sinkData = sink->sourceData();
    //ps += sinkData->flatten();
    prog = prog + sinkData->flatten();
  }

  QString functioncall;
  if (m_sinks[1]->sourceData()->format() == Data::DataBlock){
    functioncall = QString("%1 = map(%2, %3, %4);")
      .arg(m_sources[0]->connectedData()[0]->name())
      .arg(operation()->name())
      .arg(m_sinks[1]->sourceData()->name())
      .arg(m_sinks[0]->sourceData()->name());
  } else {
    functioncall = QString("%1 = map(%2, %3, %4);")
      .arg(m_sources[0]->connectedData()[0]->name())
      .arg(operation()->name())
      .arg(m_sinks[1]->sourceData()->expression())
      .arg(m_sinks[0]->sourceData()->name());
  }
    
  prog.second.append(functioncall);
  
  foreach(Source *source, sources()){
    QList<Data*> sourceData = source->connectedData();
    foreach (Data* sData, sourceData){
      prog = prog + sData->flatten();
    }
  }
  
  return prog;
}