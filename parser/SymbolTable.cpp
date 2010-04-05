#include <cstdio>
#include <cstdlib>
#include "SymbolTable.h"

using namespace std;

SymbolTable::SymbolTable() {}; // do nothing

/********************************
 * Function: addEntry
 * ------------------
 * Add an entry into the symbol table after checking that it's not already in
 * there
 *
 * Inputs:
 *    name: name of function, variable, etc
 *    category: FUNCTION, VARIABLE, etc
 *    type: INT, FLOAT, STRING, etc
 *    scope: scoping level. Defaults to zero. We may not run into scoping
 *           issues, but if we do, it's here
 */
void SymbolTable::addEntry(string name, int category, int type, int scope){
  if (isInSymtab(name)){
    fprintf(stderr, "\"%s\" already in symbol table\n", name.c_str());
    exit(2);
  }

  SymbolEntry symentry;
  symentry.name = name;
  symentry.category = category;
  symentry.type = type;
  symentry.scope = scope;
  symtab.push_back(symentry);
} 


/********************************
 * Function: isInSymtab
 * --------------------
 * Checks if entry is in symbol table
 *
 * Input:
 *    name: name of function, variable, etc
 */
bool SymbolTable::isInSymtab(string name){
  for (unsigned int i=0; i<symtab.size(); i++){
    if (name == symtab[i].name){
      return true;
    }
  }
  return false;
}

/********************************
 * Function: getTypeInSymtab
 * -------------------------
 * Grabs the type of an entry in the symbol table
 *
 * Input:
 *    name: name of function, variable, etc
 * TODO: throw an exception instead of returning -1
 */
int SymbolTable::getTypeInSymtab(string name){
  for (unsigned int i=0; i<symtab.size(); i++){
    if (name == symtab[i].name)
      return symtab[i].type;
  }
  return -1;
}


/********************************
 * Function: getIdxInSymtab
 * ------------------------
 * Return index of an entry in symbol table
 *
 * Input:
 *    name: name of function, variable, etc
 */
int SymbolTable::getIdxInSymtab(string name){
  for (unsigned int i=0; i<symtab.size(); i++){
    if (name == symtab[i].name)
      return i;
  }
  return -1;
}

/********************************
 * Function: print
 * ---------------
 * Prints out entries in symbol table in a human-readable way
 */
void SymbolTable::print(){
  printf("[idx]\tname\tcategory\ttype\tscope\n");
  printf("-----\t----\t--------\t----\t-----\n");
  for (unsigned int i=0; i<symtab.size(); i++){
    printf("[%d]\t%s\t%d\t\t%d\t%d\n",
        i,
        symtab[i].name.c_str(),
        symtab[i].category,
        symtab[i].type,
        symtab[i].scope);
  }
}