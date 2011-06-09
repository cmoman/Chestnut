/* Parser for Chestnut Code
 * ------------------------
 * Defines all valid syntax in
 * Chestnut code.
 */

%{
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <iostream>
#include <vector>
#include <sstream>
#include "SymbolTable.h"
#include "ParseUtils.h"

using namespace std;

int yyparse(void);
int yylex(void);

ParseUtils parseutils("chestnut");

// variable declaration helper struct
struct vardec_helper {
  int op;
  string fname;
  string rows;
  string cols;
  string expr;
};
vardec_helper curVarDec;

// operations used in op field
// of vardec_helper
enum vardec_ops {
  VARDEC_NOOP = 10,
  VARDEC_READ,
  VARDEC_FOREACH,
  VARDEC_VECTOR,
  VARDEC_SCALAR
};

void yyerror(const char *str)
{
	fprintf(stderr,"error: %s\n",str);
  exit(1);
}

int yywrap()
{
	return 1;
}

int main()
{
  parseutils.initializeIncludes();
  parseutils.initializeMain();

  yyparse();

  parseutils.finalizeMain();

  parseutils.writeAllFiles();

  return 0;
}
%}

%token 
TOKREAD TOKWRITE TOKPRINT TOKPRINT1D 
TOKTIMER TOKSTART TOKSTOP
TOKMAP TOKREDUCE TOKSORT
TOKFOREACH
TOKVECTOR TOKSCALAR
EQUALS SEMICOLON LPAREN RPAREN LBRACE RBRACE QUOTE COMMA
TOKROW TOKCOL TOKMAXROWS TOKMAXCOLS


%union 
{
	int number;
	char *string;
}

%token <number> STATE
%token <string> NUMBER
%token <string> ID
%token <string> FNAME
%token <string> TOKINT
%token <string> TOKFLOAT
%token <string> TOKSTRING
%token <string> TOKCPP
%token <string> ASSIGN
%token <string> PLUS
%token <string> MINUS
%token <string> MULT
%token <string> DIV
%token <string> MOD
%token <string> LT 
%token <string> LTEQ
%token <string> GT 
%token <string> GTEQ 
%token <string> NOT 
%token <string> NEQ 
%token <string> OR 
%token <string> AND

%type <string> type
%type <string> op
%type <string> filename
%type <string> alphanumeric
%type <string> read_data
%type <string> expr
%type <string> sort_comparators

%right ASSIGN
%left PLUS MINUS
%left MULT DIV MOD

%%

commands: /* empty */
	| commands command SEMICOLON
;

command:
  map_call | reduce_call | sort_call | write_call | variable_declarations | print | timer_start | timer_stop

variable_declarations:
  type ID variable_declarations_end
  {
    string type = $1;
    string name = $2;
    string fname, rows, cols, expr;

    switch (curVarDec.op){
      
      case VARDEC_READ:
        fname = curVarDec.fname;
        parseutils.makeReadDatafile(fname, name, type);
        break;
        
      case VARDEC_FOREACH:
        rows = curVarDec.rows;
        cols = curVarDec.cols;
        expr = curVarDec.expr;

        parseutils.makeForeach(name, type, rows, cols, expr);
        break;
    
      case VARDEC_VECTOR: 
        parseutils.makeVector(name, type);
        break;
        
      case VARDEC_SCALAR:
        parseutils.makeScalar(name, type);
        break;
        
    }
  
    printf("variable declaration %s %s\n", type.c_str(), name.c_str());
    free($1); free($2);
  }
  | TOKTIMER ID
  {
    string timer = $2;
    parseutils.makeTimer(timer);
    printf("timer declared: %s\n",timer.c_str());
    free($2);
  }


variable_declarations_end: 
  /* empty */ { curVarDec.op = VARDEC_NOOP; }
  | TOKVECTOR { curVarDec.op = VARDEC_VECTOR; }
  | TOKSCALAR { curVarDec.op = VARDEC_SCALAR; }
  | read_data
  | foreach

read_data:
  TOKREAD LPAREN filename RPAREN
  {
    curVarDec.op = VARDEC_READ;
    curVarDec.fname = $3;
    delete [] $3;
  }

foreach:
  NUMBER NUMBER TOKFOREACH LPAREN expr RPAREN
  {
    curVarDec.op = VARDEC_FOREACH;
    curVarDec.rows = $1;
    curVarDec.cols = $2;
    curVarDec.expr = $5;
    free($1); free($2); free($5);
  }

write_call:
  TOKWRITE LPAREN ID COMMA filename RPAREN
  {
    string object = $3;
    string fname = $5;
    parseutils.makeWriteDatafile(fname, object);
    printf("Write >\tObject: %s, OutFile: %s\n", $3, $5);
    free($3); free($5);
  }

map_call:
  ID ASSIGN TOKMAP LPAREN op COMMA alphanumeric COMMA ID RPAREN
  {
    string op = $5;
    string alter = $7;
    string source = $9;
    string destination = $1;

    string fcnname = "map";

    parseutils.makeMap(source, destination, op, alter);
    printf("Map >\tOperation: %s, Number: %s, Object: %s\n", $5, $7, $9);
    free($1); free($2); free($5); delete [] $7; free($9);
  }

reduce_call:
  ID ASSIGN TOKREDUCE LPAREN op COMMA ID RPAREN
  {
    string source = $7;
    string destination = $1;
    string op = $5;
    
    printf("Reduce >\t Src: %s, Dest: %s, Op: %s\n",
           $7, $1, $5);

    parseutils.makeReduce(source, destination, op);

    free($1); free($2); free($5); free($7);
  }

sort_call:
  ID ASSIGN TOKSORT LPAREN sort_comparators COMMA ID RPAREN
  {
    string source = $7;
    string destination = $1;
    string comparator = $5;

    parseutils.makeSort(source, destination, comparator);
    free($1); free($2); free($5); free($7);
  }

sort_comparators:
  LT | LTEQ | GT | GTEQ
  {
    $$=$1;
  }

print: printdata | printdata1D

printdata:
  TOKPRINT ID
  {
    string object = $2;
    parseutils.makePrintData(object);
    free($2);
  }

printdata1D:
  TOKPRINT1D ID
  {
    string object = $2;
    parseutils.makePrintData1D(object);
    free($2);
  }

timer_start:
  ID TOKSTART
  {
    string timer = $1;
    parseutils.makeTimerStart(timer);
    printf("timer start: %s\n",timer.c_str());
    free($1);
  }
  
timer_stop:
  ID TOKSTOP
  {
    string timer = $1;
    parseutils.makeTimerStop(timer);
    printf("timer stop: %s\n",timer.c_str());
    free($1);
  }

alphanumeric: 
  ID | NUMBER
  {
    // need to convert ID | NUMBER to a string
    stringstream ss; ss << $1;
    string str = ss.str();
    char* chstr = new char[str.length()+1];
    strcpy (chstr, str.c_str());
    free($1);
    $$ = chstr;
  }

filename: FNAME
  {
    string fname = $1;
    fname = fname.substr(1,fname.length()-2);
    char *str = new char[fname.length()+1];
    strcpy(str, fname.c_str());    
    printf("found file name: %s\n", fname.c_str());
    free($1);
    $$=str;
  }

type: TOKINT | TOKFLOAT | TOKSTRING

op: PLUS | MINUS | MULT | DIV
  { 
    printf("found op %s\n", $1);
  }
  

/*******************
 * Expressions! 
 *******************/

expr:
    expr ASSIGN expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | expr PLUS expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | expr MINUS expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | expr MULT expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | expr DIV expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | expr MOD expr
{ 
  char *str = (char*) malloc(
      sizeof(char)*(strlen($1)+strlen($2)+strlen($3)+1));
  strcpy(str,$1);
  strcat(str,$2);
  strcat(str,$3);
  free($1); free($2); free($3);
  $$=str;
}
  | LPAREN expr RPAREN
{
  char *str = (char*) malloc(
      sizeof(char)*(strlen("(")+strlen($2)+strlen(")")+1));
  strcpy(str,"(");
  strcat(str,$2);
  strcat(str,")");
  free($2);
  $$=str;
}
  | NUMBER { $$=$1; }
  | ID { $$=$1; }