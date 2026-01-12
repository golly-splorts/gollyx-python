#ifndef GOLLY_H
#define GOLLY_H

#include "json_helper.h"
#include <stdbool.h>

// Data Structures

typedef struct {
    int y;
    int *xs;
    int count;
    int capacity;
} Row;

typedef struct {
    Row *rows;
    int count;
    int capacity;
} State;

typedef struct Node {
    long long key; // packed x,y
    int value; 
    struct Node *next;
} Node;

typedef struct {
    Node **buckets;
    int size;
    int count;
} HashMap; // Also used as HashSet (value ignored)

// Common Logic

void state_init(State *state);
void state_free(State *state);
void state_copy(State *src, State *dst); 
void state_clear(State *state);
void state_add_cell(State *state, int x, int y); 
void state_remove_cell(State *state, int x, int y); 
bool state_has_cell(State *state, int x, int y); 
int state_count(State *state);

void hashmap_init(HashMap *map, int size);
void hashmap_free(HashMap *map);
void hashmap_clear(HashMap *map);
void hashmap_add(HashMap *map, int x, int y); // Set-like add
void hashmap_incr(HashMap *map, int x, int y); // Map-like incr
int hashmap_get(HashMap *map, int x, int y);
bool hashmap_contains(HashMap *map, int x, int y);
void hashmap_copy(HashMap *src, HashMap *dst);

// Simulation Structs

typedef struct {
    int rows;
    int columns;
    int periodic;
    int generation;
    bool running;
    bool halt;
    bool found_victor;
    int who_won; // 1 or 2, 0 if none/draw
    
    int *rule_b;
    int rule_b_len;
    int *rule_s;
    int rule_s_len;
} SimBase;

typedef struct {
    SimBase base;
    State actual_state;
    State actual_state1;
    State actual_state2;
    
    int maxdim;
    double *running_avg_window;
    int window_idx;
    int window_filled;
    double running_avg_last3[3];
    
    // For display/stats
    double victory;
    double coverage;
    double territory1;
    double territory2;
    int livecells;
    int livecells1;
    int livecells2;
} ToroidalSim;

typedef struct {
    SimBase base;
    
    State actual_state;
    HashMap *actual_state_colors[3]; 
    
    // dead_wait_n[level] -> State*
    State **dead_wait_n; 
    // dead_wait_colors_n[level][color] -> HashMap*
    HashMap ***dead_wait_colors_n; 
    
    int rule_c;
    int maxdim;
    
    double *running_avg_window;
    int window_idx;
    int window_filled;
    double running_avg_last3[3];
    
    double tol_zero;
    double tol_stable;
    
    double coverage;
    int livecells;
} StarSim;

// Public API

ToroidalSim* toroidal_new(JsonValue *config);
JsonValue* toroidal_step(ToroidalSim *sim);
void toroidal_free(ToroidalSim *sim);

StarSim* star_new(JsonValue *config);
JsonValue* star_step(StarSim *sim);
void star_free(StarSim *sim);

#endif