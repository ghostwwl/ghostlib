/*************************************************************************************************
 * Note: The Artxun TTserver Tool! Use to control the TTserver DataBase on remote!
 *              Copyright (C) 2011 Artxun.com
 * Author : wule
 * Date   : 2011.6
 *************************************************************************************************/


#include <tculog.h>
#include <tcrdb.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include "myconf.h"

#define REQHEADMAX     32                // maximum number of request headers of HTTP
#define MINIBNUM       31                // bucket number of map for trivial use


/* global variables */
const char *g_progname;                  // program name


/* function prototypes */
int main(int argc, char **argv);
static void usage(void);
static void printerr(TCRDB *rdb);
static int sepstrtochr(const char *str);
static char *strtozsv(const char *str, int sep, int *sp);
static int printdata(const char *ptr, int size, bool px, int sep);
static char *mygetline(FILE *ifp);
static bool myopen(TCRDB *rdb, const char *host, int port);
static bool mysetmst(TCRDB *rdb, const char *host, int port, uint64_t ts, int opts);
static int pproclist(const char *host, int port, int sep, int max, bool pv, bool px,
                    const char *fmstr);
static int procext(const char *host, int port, const char *func, int opts,
                   const char *kbuf, int ksiz, const char *vbuf, int vsiz, int sep,
                   bool px, bool pz);
static int procoptimize(const char *host, int port, const char *params);
static int do_delall(int argc, char **argv);
static int delall(const char *host, int port);
static int grunlist(int argc, char **argv);
static int dooptimize(int argc, char **argv);

int main(int argc, char **argv){
  g_progname = argv[0];
  signal(SIGPIPE, SIG_IGN);
  
  if(argc < 2) usage();
  int rv = 0;
  if(!strcmp(argv[1], "clear")){
    rv = grunlist(argc, argv);
  } 
  else if(!strcmp(argv[1], "optimize")){
    rv = dooptimize(argc, argv);
  } 
  else if(!strcmp(argv[1], "delall")){
    rv = do_delall(argc, argv);
  } 
  else {
    usage();
  }
  return rv;
  
}


static void usage(void){
  fprintf(stderr, "The Artxun TTserver Tool\n");
  fprintf(stderr, "Copyright (C) 2011 Artxun.com\n");
  fprintf(stderr, "clear  --> clear the timeout record!\n");
  fprintf(stderr, "delall --> del all record!\n");
  fprintf(stderr, "optimize --> optimize the ttserver database file!\n");
  fprintf(stderr, "\n");
  fprintf(stderr, "usage:\n");
  fprintf(stderr, "  %s clear [-port num] [-sep chr] [-m num] [-pv] [-px] [-fm str] host\n",
          g_progname);
  fprintf(stderr, "  %s optimize [-port num] host [params]\n", g_progname);
  fprintf(stderr, "  %s delall [-port num] host\n", g_progname);
  fprintf(stderr, "\n");
  exit(1);
}




static void printerr(TCRDB *rdb){
  int ecode = tcrdbecode(rdb);
  fprintf(stderr, "%s: error: %d: %s\n", g_progname, ecode, tcrdberrmsg(ecode));
}


static int sepstrtochr(const char *str){
  if(!strcmp(str, "\\t")) return '\t';
  if(!strcmp(str, "\\r")) return '\r';
  if(!strcmp(str, "\\n")) return '\n';
  return *(unsigned char *)str;
}


static char *strtozsv(const char *str, int sep, int *sp){
 int size = strlen(str);
 char *buf = tcmemdup(str, size);
 for(int i = 0; i < size; i++){
   if(buf[i] == sep) buf[i] = '\0';
 }
 *sp = size;
 return buf;
}


static int printdata(const char *ptr, int size, bool px, int sep){
  int len = 0;
  while(size-- > 0){
    if(px){
      if(len > 0) putchar(' ');
      len += printf("%02X", *(unsigned char *)ptr);
    } else if(sep > 0){
      if(*ptr == '\0'){
        putchar(sep);
      } else {
        putchar(*ptr);
      }
      len++;
    } else {
      putchar(*ptr);
      len++;
    }
    ptr++;
  }
  return len;
}


static char *mygetline(FILE *ifp){
  int len = 0;
  int blen = 1024;
  char *buf = tcmalloc(blen);
  bool end = true;
  int c;
  while((c = fgetc(ifp)) != EOF){
    end = false;
    if(c == '\0') continue;
    if(blen <= len){
      blen *= 2;
      buf = tcrealloc(buf, blen + 1);
    }
    if(c == '\n' || c == '\r') c = '\0';
    buf[len++] = c;
    if(c == '\0') break;
  }
  if(end){
    tcfree(buf);
    return NULL;
  }
  buf[len] = '\0';
  return buf;
}


static bool myopen(TCRDB *rdb, const char *host, int port){
  bool err = false;
  if(strchr(host, ':') || strchr(host, '#')){
    if(!tcrdbopen2(rdb, host)) err = true;
  } else {
    if(!tcrdbopen(rdb, host, port)) err = true;
  }
  return !err;
}


static bool mysetmst(TCRDB *rdb, const char *host, int port, uint64_t ts, int opts){
  bool err = false;
  if(strchr(host, ':')){
    if(!tcrdbsetmst2(rdb, host, ts, opts)) err = true;
  } else {
    if(!tcrdbsetmst(rdb, host, port, ts, opts)) err = true;
  }
  return !err;
}




static int grunlist(int argc, char **argv){
  char *host = NULL;
  int port = TTDEFPORT;
  int sep = -1;
  int max = -1;
  bool pv = true;
  bool px = false;
  char *fmstr = NULL;
  for(int i = 2; i < argc; i++){
    if(!host && argv[i][0] == '-'){
      if(!strcmp(argv[i], "-port")){
        if(++i >= argc) usage();;
        port = tcatoi(argv[i]);
      } else if(!strcmp(argv[i], "-sep")){
        if(++i >= argc) usage();;
        sep = sepstrtochr(argv[i]);
      } else if(!strcmp(argv[i], "-m")){
        if(++i >= argc) usage();;
        max = tcatoi(argv[i]);
      } else if(!strcmp(argv[i], "-pv")){
        pv = true;
      } else if(!strcmp(argv[i], "-px")){
        px = true;
      } else if(!strcmp(argv[i], "-fm")){
        if(++i >= argc) usage();;
        fmstr = NULL;
      } else {
        usage();
      }
    } else if(!host){
      host = argv[i];
    } else {
      usage();
    }
  }
  if(!host) usage();
  int rv = pproclist(host, port, sep, max, pv, px, fmstr);
  return rv;
}



static int pproclist(const char *host, int port, int sep, int max, bool pv, bool px,
                    const char *fmstr){
  TCRDB *rdb = tcrdbnew();
  if(!myopen(rdb, host, port)){
    printerr(rdb);
    tcrdbdel(rdb);
    return 1;
  }
  bool err = false;
  if(fmstr){
    TCLIST *keys = tcrdbfwmkeys2(rdb, fmstr, max);
    for(int i = 0; i < tclistnum(keys); i++){
      int ksiz;
      const char *kbuf = tclistval(keys, i, &ksiz);
      //printdata(kbuf, ksiz, px, sep);
      if(pv){
        int vsiz;
        char *vbuf = tcrdbget(rdb, kbuf, ksiz, &vsiz);
        if(vbuf){
              char vTimeHead[11] = {'\0'};
              time_t cur_time;
              time ( &cur_time );
              strncpy(vTimeHead, vbuf, 10);
              int vTimeStamp = atoi(vTimeHead);
              if(vTimeStamp > 0 && cur_time >= vTimeStamp){
                    printf("find [ ");
                    printdata(kbuf, ksiz, px, sep);
                    printf(" ] timestamp [ %d ]", vTimeStamp);
                    if(tcrdbout(rdb, kbuf, ksiz)){
                       printf(" del one timeout ok!\n");
                    }
                    else{printf(" del one timeout failed!\n");}
              }
          tcfree(vbuf);
        }
      }
      putchar('\n');
    }
    tclistdel(keys);
  } else {
    if(!tcrdbiterinit(rdb)){
      printerr(rdb);
      err = true;
    }
    int ksiz;
    char *kbuf;
    int cnt = 0;
    while((kbuf = tcrdbiternext(rdb, &ksiz)) != NULL){
      //printdata(kbuf, ksiz, px, sep);
      if(pv){
        int vsiz;
        char *vbuf = tcrdbget(rdb, kbuf, ksiz, &vsiz);
        if(vbuf){
              //add by wule
              char vTimeHead[11] = {'\0'};
              time_t cur_time;
              time ( &cur_time );
              strncpy(vTimeHead, vbuf, 10);
              int vTimeStamp = atoi(vTimeHead);
              //printf("cT: %d", cur_time);
              if(vTimeStamp > 0 && cur_time >= vTimeStamp){
                    printf("find [ ");
                    printdata(kbuf, ksiz, px, sep);
                    printf(" ] timestamp [ %d ]", vTimeStamp);
                    if(tcrdbout(rdb, kbuf, ksiz)){
                       printf(" del one timeout ok\n");
                    }
                    else{printf(" del one timeout failed\n");}
              }
              //end add
              //putchar('\t');
              //printdata(vbuf, vsiz, px, sep);
              tcfree(vbuf);
        }
      }
      putchar('\n');
      tcfree(kbuf);
      if(max >= 0 && ++cnt >= max) break;
    }
  }
  if(!tcrdbclose(rdb)){
    if(!err) printerr(rdb);
    err = true;
  }
  tcrdbdel(rdb);
  return err ? 1 : 0;
}

static int do_delall(int argc, char **argv){
  char *host = NULL;
  int port = TTDEFPORT;
  for(int i = 2; i < argc; i++){
    if(!host && argv[i][0] == '-'){
      if(!strcmp(argv[i], "-port")){
        if(++i >= argc) usage();
        port = tcatoi(argv[i]);
      } else {
        usage();
      }
    } else if(!host){
      host = argv[i];
    } else {
      usage();
    }
  }
  if(!host) usage();
  int rv = delall(host, port);
  return rv;
}


static int delall(const char *host, int port){
  TCRDB *rdb = tcrdbnew();
  if(!myopen(rdb, host, port)){
    printerr(rdb);
    tcrdbdel(rdb);
    return 1;
  }
  bool err = false;
  if(!tcrdbvanish(rdb)){
    printerr(rdb);
    err = true;
  }
  if(!tcrdbclose(rdb)){
    if(!err) printerr(rdb);
    err = true;
  }
  tcrdbdel(rdb);
  return err ? 1 : 0;
}

static int dooptimize(int argc, char **argv){
  char *host = NULL;
  char *params = NULL;
  int port = TTDEFPORT;
  for(int i = 2; i < argc; i++){
    if(!host && argv[i][0] == '-'){
      if(!strcmp(argv[i], "-port")){
        if(++i >= argc) usage();
        port = tcatoi(argv[i]);
      } else {
        usage();
      }
    } else if(!host){
      host = argv[i];
    } else if(!params){
      params = argv[i];
    } else {
      usage();
    }
  }
  if(!host) usage();
  int rv = procoptimize(host, port, params);
  return rv;
}

/* perform optimize command */
static int procoptimize(const char *host, int port, const char *param){
  TCRDB *rdb = tcrdbnew();
  if(!myopen(rdb, host, port)){
    printerr(rdb);
    tcrdbdel(rdb);
    return 1;
  }
  bool err = false;
  if(!tcrdboptimize(rdb, param)){
    printerr(rdb);
    err = true;
  }
  if(!tcrdbclose(rdb)){
    if(!err) printerr(rdb);
    err = true;
  }
  tcrdbdel(rdb);
  return err ? 1 : 0;
}

// END OF FILE
