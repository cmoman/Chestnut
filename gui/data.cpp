#include "data.h"


Data::Data(const QString& name, Data::Format format, const QString &datatype)
  : Object(0)
{
  m_format = format;
  m_datatype = datatype;
  m_name = name;
}

Data::~Data()
{

}

bool Data::isData() const
{
  return true;
}

bool Data::isInitialized() const
{
  // if sources to data have no connections, 
  // then nothing is feeding into them
  QList<Source*> dataSources = sources();
  return true;
}


QString Data::name() const
{
  return m_name;
}

Data::Format Data::format() const
{
  return m_format;
}

QString Data::datatype() const
{
  return m_datatype;
}

QString Data::tempData(Data::Format f) {
  static int counter = 0;
  counter++;
  switch (f) {
    case Data::Value:
      return QString("tempScalar%1").arg(counter);
    case Data::DataBlock:
      return QString("tempVector%1").arg(counter);
  }
}
