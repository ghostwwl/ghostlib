#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void *thread_function(void *arg);

char message[100] = "Hello Ghostwwl!";

int main(int argc, char **argv)
{
    int res;
    pthread_t a_thread;
    void *thread_result;
    res = pthread_create(&a_thread, NULL, thread_function, (void *)message);
    if (res != 0)
    {
        perror("Thread creation failed");
        exit(EXIT_FAILURE);
    }
    printf("Waiting for thread to finish...\n");
    
    res = pthread_join(a_thread, &thread_result); //pthread_join 阻塞执行的线程直到某线程结束
    if (res != 0)
    {
        perror("Thread join failed");
        exit(EXIT_FAILURE);
    }
    printf("Thread joined, it returned %s\n", (char *)thread_result);
    printf("Message is now %s\n", message);
    exit(EXIT_SUCCESS);
}


void *thread_function(void *arg)
{
        printf("thread_function is running. Argument was %s\n", (char *)arg);
        Sleep(3);
        strcpy(message, "Bye!");
        pthread_exit((void *)"Thank you for the CPU time");
}
