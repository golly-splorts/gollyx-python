#include <stdlib.h>
#include <string.h>
#include "golly.h"

// --- State (Sparse Matrix) ---

void state_init(State *state) {
    state->count = 0;
    state->capacity = 8;
    state->rows = malloc(state->capacity * sizeof(Row));
}

void state_free(State *state) {
    if (!state->rows) return;
    for (int i = 0; i < state->count; i++) {
        free(state->rows[i].xs);
    }
    free(state->rows);
    state->count = 0;
    state->capacity = 0;
    state->rows = NULL;
}

void state_clear(State *state) {
    if (!state->rows) return;
    for (int i = 0; i < state->count; i++) {
        free(state->rows[i].xs);
    }
    state->count = 0;
}

// Binary search for row index
static int find_row(State *state, int y, bool *found) {
    int l = 0, r = state->count - 1;
    while (l <= r) {
        int m = l + (r - l) / 2;
        if (state->rows[m].y == y) {
            *found = true;
            return m;
        }
        if (state->rows[m].y < y) l = m + 1;
        else r = m - 1;
    }
    *found = false;
    return l; // Insert position
}

// Binary search for x in row
static int find_x(Row *row, int x, bool *found) {
    int l = 0, r = row->count - 1;
    while (l <= r) {
        int m = l + (r - l) / 2;
        if (row->xs[m] == x) {
            *found = true;
            return m;
        }
        if (row->xs[m] < x) l = m + 1;
        else r = m - 1;
    }
    *found = false;
    return l;
}

void state_add_cell(State *state, int x, int y) {
    bool found_row;
    int r_idx = find_row(state, y, &found_row);
    
    if (!found_row) {
        // Insert new row
        if (state->count == state->capacity) {
            state->capacity = (state->capacity == 0) ? 8 : state->capacity * 2;
            state->rows = realloc(state->rows, state->capacity * sizeof(Row));
        }
        // Shift
        if (r_idx < state->count) {
            memmove(&state->rows[r_idx + 1], &state->rows[r_idx], (state->count - r_idx) * sizeof(Row));
        }
        state->rows[r_idx].y = y;
        state->rows[r_idx].count = 0;
        state->rows[r_idx].capacity = 4;
        state->rows[r_idx].xs = malloc(4 * sizeof(int));
        state->count++;
    }
    
    Row *row = &state->rows[r_idx];
    bool found_x;
    int c_idx = find_x(row, x, &found_x);
    
    if (!found_x) {
        if (row->count == row->capacity) {
            row->capacity *= 2;
            row->xs = realloc(row->xs, row->capacity * sizeof(int));
        }
        if (c_idx < row->count) {
            memmove(&row->xs[c_idx + 1], &row->xs[c_idx], (row->count - c_idx) * sizeof(int));
        }
        row->xs[c_idx] = x;
        row->count++;
    }
}

void state_remove_cell(State *state, int x, int y) {
    bool found_row;
    int r_idx = find_row(state, y, &found_row);
    if (!found_row) return;

    Row *row = &state->rows[r_idx];
    bool found_x;
    int c_idx = find_x(row, x, &found_x);
    if (found_x) {
        if (row->count == 1) {
            // Remove row
            free(row->xs);
            if (r_idx < state->count - 1) {
                memmove(&state->rows[r_idx], &state->rows[r_idx + 1], (state->count - r_idx - 1) * sizeof(Row));
            }
            state->count--;
        } else {
            // Remove x
            if (c_idx < row->count - 1) {
                memmove(&row->xs[c_idx], &row->xs[c_idx + 1], (row->count - c_idx - 1) * sizeof(int));
            }
            row->count--;
        }
    }
}

bool state_has_cell(State *state, int x, int y) {
    bool found_row;
    int r_idx = find_row(state, y, &found_row);
    if (!found_row) return false;
    bool found_x;
    find_x(&state->rows[r_idx], x, &found_x);
    return found_x;
}

int state_count(State *state) {
    int c = 0;
    for (int i = 0; i < state->count; i++) {
        c += state->rows[i].count;
    }
    return c;
}

void state_copy(State *src, State *dst) {
    state_clear(dst);
    if (dst->capacity < src->count) {
        free(dst->rows);
        dst->capacity = src->count + 8;
        dst->rows = malloc(dst->capacity * sizeof(Row));
    }
    dst->count = src->count;
    for (int i = 0; i < src->count; i++) {
        dst->rows[i].y = src->rows[i].y;
        dst->rows[i].count = src->rows[i].count;
        dst->rows[i].capacity = src->rows[i].count; 
        dst->rows[i].xs = malloc(dst->rows[i].capacity * sizeof(int));
        memcpy(dst->rows[i].xs, src->rows[i].xs, src->rows[i].count * sizeof(int));
    }
}

// --- HashMap ---

static unsigned int hash_key(long long key) {
    key = (~key) + (key << 18);
    key = key ^ (key >> 31);
    key = key * 21;
    key = key ^ (key >> 11);
    key = key + (key << 6);
    key = key ^ (key >> 22);
    return (unsigned int)key;
}

void hashmap_init(HashMap *map, int size) {
    map->size = size;
    map->count = 0;
    map->buckets = calloc(size, sizeof(Node*));
}

void hashmap_free(HashMap *map) {
    hashmap_clear(map);
    free(map->buckets);
    map->size = 0;
    map->buckets = NULL;
}

void hashmap_clear(HashMap *map) {
    if (!map->buckets) return;
    for (int i = 0; i < map->size; i++) {
        Node *n = map->buckets[i];
        while (n) {
            Node *next = n->next;
            free(n);
            n = next;
        }
        map->buckets[i] = NULL;
    }
    map->count = 0;
}

void hashmap_add(HashMap *map, int x, int y) {
    long long key = ((long long)y << 32) | (unsigned int)x;
    unsigned int h = hash_key(key) % map->size;
    Node *n = map->buckets[h];
    while (n) {
        if (n->key == key) return;
        n = n->next;
    }
    Node *new_node = malloc(sizeof(Node));
    new_node->key = key;
    new_node->value = 0;
    new_node->next = map->buckets[h];
    map->buckets[h] = new_node;
    map->count++;
}

void hashmap_incr(HashMap *map, int x, int y) {
    long long key = ((long long)y << 32) | (unsigned int)x;
    unsigned int h = hash_key(key) % map->size;
    Node *n = map->buckets[h];
    while (n) {
        if (n->key == key) {
            n->value++;
            return;
        }
        n = n->next;
    }
    Node *new_node = malloc(sizeof(Node));
    new_node->key = key;
    new_node->value = 1;
    new_node->next = map->buckets[h];
    map->buckets[h] = new_node;
    map->count++;
}

int hashmap_get(HashMap *map, int x, int y) {
    long long key = ((long long)y << 32) | (unsigned int)x;
    unsigned int h = hash_key(key) % map->size;
    Node *n = map->buckets[h];
    while (n) {
        if (n->key == key) return n->value;
        n = n->next;
    }
    return 0;
}

bool hashmap_contains(HashMap *map, int x, int y) {
    long long key = ((long long)y << 32) | (unsigned int)x;
    unsigned int h = hash_key(key) % map->size;
    Node *n = map->buckets[h];
    while (n) {
        if (n->key == key) return true;
        n = n->next;
    }
    return false;
}

void hashmap_copy(HashMap *src, HashMap *dst) {
    hashmap_clear(dst);
    if (dst->size == 0) hashmap_init(dst, src->size > 0 ? src->size : 1024);
    
    for (int i = 0; i < src->size; i++) {
        Node *n = src->buckets[i];
        while (n) {
            unsigned int h = hash_key(n->key) % dst->size;
            Node *new_node = malloc(sizeof(Node));
            new_node->key = n->key;
            new_node->value = n->value;
            new_node->next = dst->buckets[h];
            dst->buckets[h] = new_node;
            dst->count++;
            
            n = n->next;
        }
    }
}
