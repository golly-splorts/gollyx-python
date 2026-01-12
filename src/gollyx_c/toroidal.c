#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "golly.h"

#define SMOL 1e-12
#define EQUALTOL 1e-8

// Forward declarations
JsonValue* toroidal_get_stats(ToroidalSim *sim);
static void update_moving_avg(ToroidalSim *sim);

static char *my_strdup(const char *s) {
    if (!s) return NULL;
    size_t len = strlen(s) + 1;
    char *p = malloc(len);
    if (p) memcpy(p, s, len);
    return p;
}

static void load_state_from_json(State *state, const char *json_str, int rows, int cols, int periodic) {
    if (!json_str) return;
    JsonValue *root = json_parse(json_str);
    if (!root || root->type != JSON_ARRAY) {
        json_free(root);
        return;
    }
    for (int i = 0; i < root->data.array.count; i++) {
        JsonValue *row_obj = root->data.array.values[i];
        if (row_obj->type == JSON_OBJECT) {
            for (int k = 0; k < row_obj->data.object.count; k++) {
                char *key = row_obj->data.object.keys[k];
                int y_raw = atoi(key);
                JsonValue *xs = row_obj->data.object.values[k];
                if (xs->type == JSON_ARRAY) {
                    for (int j = 0; j < xs->data.array.count; j++) {
                         int x_raw = json_as_int(xs->data.array.values[j]);
                         int x = x_raw;
                         int y = y_raw;
                         if (periodic) {
                             x = (x % cols + cols) % cols;
                             y = (y % rows + rows) % rows;
                         }
                         state_add_cell(state, x, y);
                    }
                }
            }
        }
    }
    json_free(root);
}

static int get_cell_color(ToroidalSim *sim, int x, int y) {
    if (sim->base.periodic) {
        x = (x + sim->base.columns) % sim->base.columns;
        y = (y + sim->base.rows) % sim->base.rows;
    }
    // Check bounds if not periodic? (Code implies periodic is default True)
    if (state_has_cell(&sim->actual_state1, x, y)) return 1;
    if (state_has_cell(&sim->actual_state2, x, y)) return 2;
    return 0;
}

static bool approx_equal(double a, double b, double tol) {
    return (fabs(b - a) / fabs(a + SMOL)) < tol;
}

ToroidalSim* toroidal_new(JsonValue *config) {
    ToroidalSim *sim = calloc(1, sizeof(ToroidalSim));
    
    sim->base.rows = json_as_int(json_get(config, "rows"));
    sim->base.columns = json_as_int(json_get(config, "columns"));
    
    JsonValue *p = json_get(config, "periodic");
    sim->base.periodic = p ? json_as_bool(p) : 1; 
    
    sim->base.halt = 1; // Default to true
    JsonValue *h = json_get(config, "halt");
    if (h) {
        if (h->type == JSON_BOOL) sim->base.halt = h->data.boolean;
        else if (h->type == JSON_NUMBER) sim->base.halt = (h->data.number != 0);
    }
    
    sim->maxdim = json_as_int(json_get(config, "maxdim"));
    if (sim->maxdim <= 0) sim->maxdim = 280;
    
    JsonValue *rb = json_get(config, "rule_b");
    if (rb) {
        if (rb->type == JSON_STRING) {
             char *s = rb->data.string;
             sim->base.rule_b_len = strlen(s);
             sim->base.rule_b = malloc(sim->base.rule_b_len * sizeof(int));
             for (int i=0; i<sim->base.rule_b_len; i++) sim->base.rule_b[i] = s[i] - '0';
        } else if (rb->type == JSON_ARRAY) {
             sim->base.rule_b_len = rb->data.array.count;
             sim->base.rule_b = malloc(sim->base.rule_b_len * sizeof(int));
             for (int i=0; i<sim->base.rule_b_len; i++) sim->base.rule_b[i] = json_as_int(rb->data.array.values[i]);
        }
    } else {
        sim->base.rule_b_len = 1;
        sim->base.rule_b = malloc(sizeof(int));
        sim->base.rule_b[0] = 3;
    }

    JsonValue *rs = json_get(config, "rule_s");
    if (rs) {
        if (rs->type == JSON_STRING) {
             char *s = rs->data.string;
             sim->base.rule_s_len = strlen(s);
             sim->base.rule_s = malloc(sim->base.rule_s_len * sizeof(int));
             for (int i=0; i<sim->base.rule_s_len; i++) sim->base.rule_s[i] = s[i] - '0';
        } else if (rs->type == JSON_ARRAY) {
             sim->base.rule_s_len = rs->data.array.count;
             sim->base.rule_s = malloc(sim->base.rule_s_len * sizeof(int));
             for (int i=0; i<sim->base.rule_s_len; i++) sim->base.rule_s[i] = json_as_int(rs->data.array.values[i]);
        }
    } else {
        sim->base.rule_s_len = 2;
        sim->base.rule_s = malloc(2 * sizeof(int));
        sim->base.rule_s[0] = 2;
        sim->base.rule_s[1] = 3;
    }
    
    state_init(&sim->actual_state);
    state_init(&sim->actual_state1);
    state_init(&sim->actual_state2);
    
    const char *ic1 = json_as_string(json_get(config, "initialConditions1"));
    const char *ic2 = json_as_string(json_get(config, "initialConditions2"));
    
    if (ic1) load_state_from_json(&sim->actual_state1, ic1, sim->base.rows, sim->base.columns, sim->base.periodic);
    if (ic2) load_state_from_json(&sim->actual_state2, ic2, sim->base.rows, sim->base.columns, sim->base.periodic);
    
    for (int i=0; i<sim->actual_state1.count; i++) {
        int y = sim->actual_state1.rows[i].y;
        for (int j=0; j<sim->actual_state1.rows[i].count; j++) {
            state_add_cell(&sim->actual_state, sim->actual_state1.rows[i].xs[j], y);
        }
    }
    for (int i=0; i<sim->actual_state2.count; i++) {
        int y = sim->actual_state2.rows[i].y;
        for (int j=0; j<sim->actual_state2.rows[i].count; j++) {
            state_add_cell(&sim->actual_state, sim->actual_state2.rows[i].xs[j], y);
        }
    }
    
    sim->base.running = true;
    sim->base.generation = 0;
    
    sim->running_avg_window = calloc(sim->maxdim, sizeof(double));
    sim->window_idx = 0;
    
    // Initial stats and update moving avg
    JsonValue *stats = toroidal_get_stats(sim);
    json_free(stats);
    update_moving_avg(sim);
    
    return sim;
}

static void update_moving_avg(ToroidalSim *sim) {
    if (sim->base.found_victor) return;
    
    int maxdim = sim->maxdim;
    if (sim->base.generation < maxdim) {
        sim->running_avg_window[sim->base.generation] = sim->victory;
        sim->window_filled = sim->base.generation + 1;
    } else {
        memmove(sim->running_avg_window, sim->running_avg_window + 1, (maxdim - 1) * sizeof(double));
        sim->running_avg_window[maxdim - 1] = sim->victory;
        
        double summ = 0;
        for(int k=0; k<maxdim; k++) summ += sim->running_avg_window[k];
        double running_avg = summ / maxdim;
        
        double removed = sim->running_avg_last3[0];
        sim->running_avg_last3[0] = sim->running_avg_last3[1];
        sim->running_avg_last3[1] = sim->running_avg_last3[2];
        sim->running_avg_last3[2] = running_avg;
        
        double tol = EQUALTOL;
        if (!approx_equal(removed, 0.0, tol)) {
             bool b1 = approx_equal(sim->running_avg_last3[0], sim->running_avg_last3[1], tol);
             bool b2 = approx_equal(sim->running_avg_last3[1], sim->running_avg_last3[2], tol);
             bool zerocells = (sim->livecells1 == 0 || sim->livecells2 == 0);
             
             if ((b1 && b2) || zerocells) {
                 bool z1 = approx_equal(sim->running_avg_last3[0], 50.0, tol);
                 bool z2 = approx_equal(sim->running_avg_last3[1], 50.0, tol);
                 bool z3 = approx_equal(sim->running_avg_last3[2], 50.0, tol);
                 
                 if ((!z1 && !z2 && !z3) || zerocells) {
                     if (sim->livecells1 > sim->livecells2) {
                         sim->base.found_victor = true;
                         sim->base.who_won = 1;
                     } else if (sim->livecells1 < sim->livecells2) {
                         sim->base.found_victor = true;
                         sim->base.who_won = 2;
                     }
                 }
             }
        }
    }
}

static int get_color_from_alive_neighbors(ToroidalSim *sim, int x, int y, int *dead_neighbors_mask, int *dead_neighbors_coords) {
    int neighbors = 0;
    int neighbors1 = 0;
    int neighbors2 = 0;
    
    // Neighbors offsets
    int offsets[8][2] = {
        {-1, -1}, {0, -1}, {1, -1},
        {-1, 0},           {1, 0},
        {-1, 1},  {0, 1},  {1, 1}
    };
    
    for (int i = 0; i < 8; i++) {
        int nx = x + offsets[i][0];
        int ny = y + offsets[i][1];
        
        if (sim->base.periodic) {
             nx = (nx + sim->base.columns) % sim->base.columns;
             ny = (ny + sim->base.rows) % sim->base.rows;
        }
        
        // Dead neighbor coords tracking
        dead_neighbors_coords[i*2] = nx;
        dead_neighbors_coords[i*2+1] = ny;
        
        if (state_has_cell(&sim->actual_state, nx, ny)) {
            // Alive
            dead_neighbors_mask[i] = 0; // Not dead
            neighbors++;
            int color = get_cell_color(sim, nx, ny);
            if (color == 1) neighbors1++;
            else if (color == 2) neighbors2++;
        } else {
            // Dead
            dead_neighbors_mask[i] = 1; // Dead
        }
    }
    
    int color = 0;
    if (neighbors1 > neighbors2) color = 1;
    else if (neighbors2 > neighbors1) color = 2;
    else if ((x % 2 == 0) == (y % 2 == 0)) color = 1; 
    else color = 2;
    
    return (neighbors << 16) | color;
}

static int get_color_for_birth(ToroidalSim *sim, int x, int y) {
    if (sim->base.periodic) {
        x = (x % sim->base.columns + sim->base.columns) % sim->base.columns;
        y = (y % sim->base.rows + sim->base.rows) % sim->base.rows;
    }
    int neighbors1 = 0;
    int neighbors2 = 0;
    
    int offsets[8][2] = {
        {-1, -1}, {0, -1}, {1, -1},
        {-1, 0},           {1, 0},
        {-1, 1},  {0, 1},  {1, 1}
    };
    
    for (int i = 0; i < 8; i++) {
        int nx = x + offsets[i][0];
        int ny = y + offsets[i][1];
        
        if (sim->base.periodic) {
             nx = (nx + sim->base.columns) % sim->base.columns;
             ny = (ny + sim->base.rows) % sim->base.rows;
        }
        
        int c = get_cell_color(sim, nx, ny);
        if (c == 1) neighbors1++;
        else if (c == 2) neighbors2++;
    }
    
    if (neighbors1 > neighbors2) return 1;
    if (neighbors2 > neighbors1) return 2;
    if ((x % 2 == 0) == (y % 2 == 0)) return 1; 
    return 2;
}

JsonValue* toroidal_step(ToroidalSim *sim) {
    if (!sim->base.running || (sim->base.halt && sim->base.found_victor)) {
        sim->base.running = false;
        return toroidal_get_stats(sim);
    }
    
    sim->base.generation++;
    
    HashMap all_dead_neighbors;
    hashmap_init(&all_dead_neighbors, 1024);
    
    State new_state;
    state_init(&new_state);
    State new_state1;
    state_init(&new_state1);
    State new_state2;
    state_init(&new_state2);
    
    // Iterate over live cells
    for (int i = 0; i < sim->actual_state.count; i++) {
        int y = sim->actual_state.rows[i].y;
        for (int j = 0; j < sim->actual_state.rows[i].count; j++) {
            int x = sim->actual_state.rows[i].xs[j];
            
            int dead_mask[8];
            int dead_coords[16];
            
            int res = get_color_from_alive_neighbors(sim, x, y, dead_mask, dead_coords);
            int neighbors = res >> 16;
            int color = res & 0xFFFF;
            
            // Collect dead neighbors
            for (int k = 0; k < 8; k++) {
                if (dead_mask[k]) {
                    hashmap_incr(&all_dead_neighbors, dead_coords[k*2], dead_coords[k*2+1]);
                }
            }
            
            // Survival check
            bool survive = false;
            for (int k = 0; k < sim->base.rule_s_len; k++) {
                if (neighbors == sim->base.rule_s[k]) {
                    survive = true;
                    break;
                }
            }
            
            if (survive) {
                state_add_cell(&new_state, x, y);
                if (color == 1) state_add_cell(&new_state1, x, y);
                else if (color == 2) state_add_cell(&new_state2, x, y);
            }
        }
    }
    
    // Birth check
    for (int i = 0; i < all_dead_neighbors.size; i++) {
        Node *n = all_dead_neighbors.buckets[i];
        while (n) {
            bool birth = false;
            for (int k = 0; k < sim->base.rule_b_len; k++) {
                if (n->value == sim->base.rule_b[k]) {
                    birth = true;
                    break;
                }
            }
            
            if (birth) {
                int x = (int)(n->key & 0xFFFFFFFF);
                int y = (int)(n->key >> 32);
                
                int nx = x; 
                int ny = y;
                if (sim->base.periodic) {
                    nx = (x % sim->base.columns + sim->base.columns) % sim->base.columns;
                    ny = (y % sim->base.rows + sim->base.rows) % sim->base.rows;
                }
                
                state_add_cell(&new_state, nx, ny);
                int color = get_color_for_birth(sim, x, y);
                
                if (color == 1) state_add_cell(&new_state1, nx, ny);
                else if (color == 2) state_add_cell(&new_state2, nx, ny);
            }
            n = n->next;
        }
    }
    
    state_free(&sim->actual_state);
    state_free(&sim->actual_state1);
    state_free(&sim->actual_state2);
    hashmap_free(&all_dead_neighbors);
    
    sim->actual_state = new_state;
    sim->actual_state1 = new_state1;
    sim->actual_state2 = new_state2;
    
    JsonValue *stats = toroidal_get_stats(sim);
    update_moving_avg(sim);
    return stats;
}

JsonValue* toroidal_get_stats(ToroidalSim *sim) {
    sim->livecells = state_count(&sim->actual_state);
    sim->livecells1 = state_count(&sim->actual_state1);
    sim->livecells2 = state_count(&sim->actual_state2);
    
    sim->victory = 0.0;
    if (sim->livecells1 > sim->livecells2) {
        sim->victory = (sim->livecells1 * 100.0) / (sim->livecells1 + sim->livecells2 + SMOL);
    } else {
        sim->victory = (sim->livecells2 * 100.0) / (sim->livecells1 + sim->livecells2 + SMOL);
    }
    
    double total_area = sim->base.rows * sim->base.columns;
    sim->coverage = (sim->livecells * 100.0) / total_area;
    sim->territory1 = (sim->livecells1 * 100.0) / total_area;
    sim->territory2 = (sim->livecells2 * 100.0) / total_area;
    
    JsonValue *obj = calloc(1, sizeof(JsonValue));
    obj->type = JSON_OBJECT;
    obj->data.object.keys = malloc(16 * sizeof(char*));
    obj->data.object.values = malloc(16 * sizeof(JsonValue*));
    int c = 0;
    
    #define ADD_INT(k, v) \
        obj->data.object.keys[c] = my_strdup(k); \
        obj->data.object.values[c] = calloc(1, sizeof(JsonValue)); \
        obj->data.object.values[c]->type = JSON_NUMBER; \
        obj->data.object.values[c]->data.number = (double)(v); \
        c++;

    #define ADD_DOUBLE(k, v) \
        obj->data.object.keys[c] = my_strdup(k); \
        obj->data.object.values[c] = calloc(1, sizeof(JsonValue)); \
        obj->data.object.values[c]->type = JSON_NUMBER; \
        obj->data.object.values[c]->data.number = (v); \
        c++;
        
    ADD_INT("generation", sim->base.generation);
    ADD_INT("liveCells", sim->livecells);
    ADD_INT("liveCells1", sim->livecells1);
    ADD_INT("liveCells2", sim->livecells2);
    ADD_DOUBLE("victoryPct", sim->victory);
    ADD_DOUBLE("coverage", sim->coverage);
    ADD_DOUBLE("territory1", sim->territory1);
    ADD_DOUBLE("territory2", sim->territory2);
    
    JsonValue *l3 = calloc(1, sizeof(JsonValue));
    l3->type = JSON_ARRAY;
    l3->data.array.values = malloc(3 * sizeof(JsonValue*));
    l3->data.array.count = 3;
    for(int i=0; i<3; i++) {
        l3->data.array.values[i] = calloc(1, sizeof(JsonValue));
        l3->data.array.values[i]->type = JSON_NUMBER;
        l3->data.array.values[i]->data.number = sim->running_avg_last3[i];
    }
    obj->data.object.keys[c] = my_strdup("last3");
    obj->data.object.values[c] = l3;
    c++;
    
    obj->data.object.count = c;
    return obj;
}

void toroidal_free(ToroidalSim *sim) {
    state_free(&sim->actual_state);
    state_free(&sim->actual_state1);
    state_free(&sim->actual_state2);
    free(sim->base.rule_b);
    free(sim->base.rule_s);
    free(sim->running_avg_window);
    free(sim);
}