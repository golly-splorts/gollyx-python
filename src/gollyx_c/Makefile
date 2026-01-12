CC = gcc
CFLAGS = -O3 -Wall -Wextra
TARGET = gollyx_c
SRCS = main.c json_helper.c sim_utils.c toroidal.c star.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ -lm

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
