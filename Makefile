# Makefile

CC = gcc
CFLAGS = -Wall
LDFLAGS = -lopenblas
TARGET = out
SRC = main.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

new: clean all run
