/***************************************************
 * Read my telbook from sqlite database
 * CopyRight: Ghostwwl
 * Email    : gostwwl@gmail.com
 ***************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>

int main(int argc, char* argv[])
{
    sqlite3 *db;
    char *szErrMsg = 0;
    int rc, irow = 0, icolumn = 0;
    int i, j;
    char ** szResult;
    char strSQL[1024]="";
    int a=0;
    char dbfile[128];
    
    printf ("Please Input The SqliteDB Full Name:");
    if (fgets (dbfile, sizeof(dbfile), stdin) == NULL)
    {
	 exit(0);
    }
        
    rc = sqlite3_open(dbfile, &db);
    if( rc )
    {
        fprintf(stderr, "Can't open database: %sn", sqlite3_errmsg(db));
        sqlite3_close(db);
        exit(1);
    }
    
    rc = sqlite3_exec(db, "BEGIN;", 0, 0, &szErrMsg);

    sqlite3_get_table(db, "SELECT * FROM thread limit 1000;", &szResult, &irow,
		    &icolumn, &szErrMsg);
    printf("\nname      mobile\n");
    printf("-------------------------------\n");
    for( i = 1; i <= irow; i++)
    {
         printf(szResult[i*icolumn]);
    }

    sqlite3_free_table(szResult);

    rc = sqlite3_exec(db, "COMMIT;", 0, 0, &szErrMsg); 
    sqlite3_close(db);
    system("pause");
    return 0;
}
