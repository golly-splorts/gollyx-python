#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "golly.h"

#define SMOL 1e-12

// Forward decls
JsonValue* star_get_stats(StarSim *sim);
static void update_moving_avg(StarSim *sim);
static int get_cell_color_alive(StarSim *sim, int x, int y);

static char *my_strdup(const char *s) {
    if (!s) return NULL;
    size_t len = strlen(s) + 1;
    char *p = malloc(len);
    if (p) memcpy(p, s, len);
    return p;
}

static void load_state_from_json(State *state, HashMap **colors, const char *json_str, int color_idx, int rows, int cols, int periodic) {
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
                         if (colors) hashmap_add(colors[color_idx], x, y);
                    }
                }
            }
        }
    }
    json_free(root);
}

static bool approx_equal(double a, double b, double tol) {
    double denom = fabs(a);
    if (fabs(b) > denom) denom = fabs(b);
    if (SMOL > denom) denom = SMOL;
    return (fabs(b - a) / denom) < tol;
}

static int periodic_x(StarSim *sim, int x) {
    return (x % sim->base.columns + sim->base.columns) % sim->base.columns;
}
static int periodic_y(StarSim *sim, int y) {
    return (y % sim->base.rows + sim->base.rows) % sim->base.rows;
}

StarSim* star_new(JsonValue *config) {
    StarSim *sim = calloc(1, sizeof(StarSim));
    
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
    
    sim->rule_c = json_as_int(json_get(config, "rule_c"));
    if (sim->rule_c < 3) sim->rule_c = 4;
    
    sim->tol_zero = 1e-8;
    sim->tol_stable = 1e-6;
    JsonValue *tz = json_get(config, "tol_zero");
    if (tz) sim->tol_zero = json_as_number(tz);
    JsonValue *ts = json_get(config, "tol_stable");
    if (ts) sim->tol_stable = json_as_number(ts);
    
    state_init(&sim->actual_state);
    for(int i=0; i<3; i++) {
        sim->actual_state_colors[i] = malloc(sizeof(HashMap));
        hashmap_init(sim->actual_state_colors[i], 1024);
    }
    
    int dw_levels = sim->rule_c - 2;
    sim->dead_wait_n = malloc(dw_levels * sizeof(State*));
    sim->dead_wait_colors_n = malloc(dw_levels * sizeof(HashMap**));
    for (int i=0; i<dw_levels; i++) {
        sim->dead_wait_n[i] = malloc(sizeof(State));
        state_init(sim->dead_wait_n[i]);
        sim->dead_wait_colors_n[i] = malloc(3 * sizeof(HashMap*));
        for (int j=0; j<3; j++) {
            sim->dead_wait_colors_n[i][j] = malloc(sizeof(HashMap));
            hashmap_init(sim->dead_wait_colors_n[i][j], 128);
        }
    }
    
    const char *s1 = json_as_string(json_get(config, "initialConditions1"));
    const char *s2 = json_as_string(json_get(config, "initialConditions2"));
    if (s1) load_state_from_json(&sim->actual_state, sim->actual_state_colors, s1, 0, sim->base.rows, sim->base.columns, sim->base.periodic);
    if (s2) load_state_from_json(&sim->actual_state, sim->actual_state_colors, s2, 1, sim->base.rows, sim->base.columns, sim->base.periodic);
    
    // Dead wait patterns
    const char *b1 = json_as_string(json_get(config, "initialConditionsb1"));
    const char *b2 = json_as_string(json_get(config, "initialConditionsb2"));
    const char *c1 = json_as_string(json_get(config, "initialConditionsc1"));
    const char *c2 = json_as_string(json_get(config, "initialConditionsc2"));
    
    if (dw_levels > 0) {
        if (b1) load_state_from_json(sim->dead_wait_n[0], sim->dead_wait_colors_n[0], b1, 0, sim->base.rows, sim->base.columns, sim->base.periodic);
        if (b2) load_state_from_json(sim->dead_wait_n[0], sim->dead_wait_colors_n[0], b2, 1, sim->base.rows, sim->base.columns, sim->base.periodic);
    }
    if (dw_levels > 1) {
        if (c1) load_state_from_json(sim->dead_wait_n[1], sim->dead_wait_colors_n[1], c1, 0, sim->base.rows, sim->base.columns, sim->base.periodic);
        if (c2) load_state_from_json(sim->dead_wait_n[1], sim->dead_wait_colors_n[1], c2, 1, sim->base.rows, sim->base.columns, sim->base.periodic);
    }

    
    sim->base.running = true;
    sim->base.generation = 0;
    sim->running_avg_window = calloc(sim->maxdim, sizeof(double));
    
    star_get_stats(sim);
    update_moving_avg(sim);
    
    return sim;
}

static int get_cell_color_alive(StarSim *sim, int x, int y) {
    if (sim->base.periodic) {
        x = periodic_x(sim, x);
        y = periodic_y(sim, y);
    }
    if (hashmap_contains(sim->actual_state_colors[0], x, y)) return 1;
    if (hashmap_contains(sim->actual_state_colors[1], x, y)) return 2;
    if (hashmap_contains(sim->actual_state_colors[2], x, y)) return 3;
    return 0;
}

static bool is_dead_wait(StarSim *sim, int x, int y) {
    if (sim->base.periodic) {
        x = periodic_x(sim, x);
        y = periodic_y(sim, y);
    }
    for (int i=0; i < sim->rule_c - 2; i++) {
        for (int c=0; c<3; c++) {
            if (hashmap_contains(sim->dead_wait_colors_n[i][c], x, y)) return true;
        }
    }
    return false;
}

static void get_neighbors_info(StarSim *sim, int x, int y, int *neighbors_out, int *color_out, int *dead_neighbors_coords, int *dead_neighbors_valid) {
    int neighbors_colors[3] = {0, 0, 0};
    int offsets[8][2] = {
        {-1, -1}, {0, -1}, {1, -1},
        {-1, 0},           {1, 0},
        {-1, 1},  {0, 1},  {1, 1}
    };
    
    for (int i = 0; i < 8; i++) {
        int nx = x + offsets[i][0];
        int ny = y + offsets[i][1];
        
        if (sim->base.periodic) {
             nx = periodic_x(sim, nx);
             ny = periodic_y(sim, ny);
        }
        
        dead_neighbors_coords[i*2] = nx;
        dead_neighbors_coords[i*2+1] = ny;
        
        int c = get_cell_color_alive(sim, nx, ny);
        if (c > 0) {
            neighbors_colors[c-1]++;
            dead_neighbors_valid[i] = 0; 
        } else {
            dead_neighbors_valid[i] = 1; 
        }
    }
    
    int neighbors = neighbors_colors[0] + neighbors_colors[1] + neighbors_colors[2];
    int neighbors_norefs = neighbors_colors[0] + neighbors_colors[1];
    *neighbors_out = neighbors;
    
    int color = 0;
    if (neighbors > 0) {
        if (neighbors_norefs > 0) {
            int max_neighbor = (neighbors_colors[0] > neighbors_colors[1]) ? neighbors_colors[0] : neighbors_colors[1];
            int num_equal_max = (neighbors_colors[0] == max_neighbor) + (neighbors_colors[1] == max_neighbor);
            
            if (num_equal_max == 1) {
                color = (neighbors_colors[0] > neighbors_colors[1]) ? 1 : 2;
            } else {
                int neighbors_dw[2] = {0, 0};
                for (int dw_lvl = 0; dw_lvl < sim->rule_c - 2; dw_lvl++) {
                    for (int dc = 0; dc < 2; dc++) { 
                        for (int i=0; i<8; i++) {
                             int nx = x + offsets[i][0];
                             int ny = y + offsets[i][1];
                             if (sim->base.periodic) { nx = periodic_x(sim, nx); ny = periodic_y(sim, ny); }
                             if (hashmap_contains(sim->dead_wait_colors_n[dw_lvl][dc], nx, ny)) {
                                 neighbors_dw[dc]++;
                             }
                        }
                    }
                }
                
                int score1 = neighbors_colors[0] + neighbors_dw[0];
                int score2 = neighbors_colors[1] + neighbors_dw[1];
                if (score1 > score2) color = 1;
                else if (score2 > score1) color = 2;
                else color = -1;
            }
        } else {
            color = -1;
        }
    } else {
        color = -1;
    }
    
    if (color < 0) {
        color = get_cell_color_alive(sim, x, y);
    }
    *color_out = color;
}

static int get_color_from_alive_for_birth(StarSim *sim, int x, int y) {
    if (sim->base.periodic) {
        x = periodic_x(sim, x);
        y = periodic_y(sim, y);
    }
    int neighbors_colors[3] = {0, 0, 0};

    int offsets[8][2] = {{-1, -1}, {0, -1}, {1, -1}, {-1, 0}, {1, 0}, {-1, 1}, {0, 1}, {1, 1}};
    
    for (int i = 0; i < 8; i++) {
        int nx = x + offsets[i][0];
        int ny = y + offsets[i][1];
        if (sim->base.periodic) { nx = periodic_x(sim, nx); ny = periodic_y(sim, ny); }
        int c = get_cell_color_alive(sim, nx, ny);
        if (c > 0) neighbors_colors[c-1]++;
    }
    
    int neighbors = neighbors_colors[0] + neighbors_colors[1] + neighbors_colors[2];
    int neighbors_norefs = neighbors_colors[0] + neighbors_colors[1];
    
    if (neighbors > 0) {
        if (neighbors_norefs > 0) {
             int max_neighbor = (neighbors_colors[0] > neighbors_colors[1]) ? neighbors_colors[0] : neighbors_colors[1];
             if ((neighbors_colors[0] == max_neighbor) && (neighbors_colors[1] == max_neighbor)) return 3;
             return (neighbors_colors[0] > neighbors_colors[1]) ? 1 : 2;
        } else {
            return 3;
        }
    }
    return 3;
}

static void update_moving_avg(StarSim *sim) {
    if (sim->base.found_victor) return;
    
    double rootsum = 0;
    rootsum += sim->actual_state_colors[0]->count * sim->actual_state_colors[0]->count;
    rootsum += sim->actual_state_colors[1]->count * sim->actual_state_colors[1]->count;
    rootsum = sqrt(rootsum);
    
    int maxdim = sim->maxdim;
    if (sim->base.generation < maxdim) {
        sim->running_avg_window[sim->base.generation] = rootsum;
    } else {
        memmove(sim->running_avg_window, sim->running_avg_window + 1, (maxdim - 1) * sizeof(double));
        sim->running_avg_window[maxdim - 1] = rootsum;
        
        double summ = 0;
        for(int k=0; k<maxdim; k++) summ += sim->running_avg_window[k];
        double running_avg = summ / maxdim;
        
        double removed = sim->running_avg_last3[0];
        sim->running_avg_last3[0] = sim->running_avg_last3[1];
        sim->running_avg_last3[1] = sim->running_avg_last3[2];
        sim->running_avg_last3[2] = running_avg;
        
        if (!approx_equal(removed, 0.0, sim->tol_zero)) {
            bool b1 = approx_equal(sim->running_avg_last3[0], sim->running_avg_last3[1], sim->tol_stable);
            bool b2 = approx_equal(sim->running_avg_last3[1], sim->running_avg_last3[2], sim->tol_stable);
            
            if (b1 && b2 && sim->livecells > 0) {
                sim->base.found_victor = true;
                int c1 = sim->actual_state_colors[0]->count;
                int c2 = sim->actual_state_colors[1]->count;
                if (c1 > c2) sim->base.who_won = 1;
                else if (c1 < c2) sim->base.who_won = 2;
                else sim->base.who_won = -1;
            }
        }
    }
    
    int zero_score = 0;
    if (sim->actual_state_colors[0]->count == 0) zero_score++;
    if (sim->actual_state_colors[1]->count == 0) zero_score++;
    
    if (zero_score >= 1) {
        sim->base.found_victor = true;
        if (sim->base.generation < maxdim) {
            sim->base.who_won = -1;
        } else {
            int c1 = sim->actual_state_colors[0]->count;
            int c2 = sim->actual_state_colors[1]->count;
            if (c1 > c2) sim->base.who_won = 1;
            else if (c1 < c2) sim->base.who_won = 2;
            else sim->base.who_won = -1;
        }
    }
}

JsonValue* star_step(StarSim *sim) {
    if (!sim->base.running || (sim->base.halt && sim->base.found_victor)) {
        sim->base.running = false;
        return star_get_stats(sim);
    }
    
    sim->base.generation++;
    
    HashMap all_dead_neighbors;
    hashmap_init(&all_dead_neighbors, 1024);
    
    State new_state;
    state_init(&new_state);
    HashMap *new_colors[3];
    for(int i=0; i<3; i++) {
        new_colors[i] = malloc(sizeof(HashMap));
        hashmap_init(new_colors[i], 1024);
    }
    
    int dw_levels = sim->rule_c - 2;
    State *new_dw0_n = malloc(sizeof(State));
    state_init(new_dw0_n);
    HashMap **new_dw0_colors = malloc(3 * sizeof(HashMap*));
    for(int i=0; i<3; i++) {
        new_dw0_colors[i] = malloc(sizeof(HashMap));
        hashmap_init(new_dw0_colors[i], 128);
    }
    
    for (int i = 0; i < sim->actual_state.count; i++) {
        int y = sim->actual_state.rows[i].y;
        for (int j = 0; j < sim->actual_state.rows[i].count; j++) {
            int x = sim->actual_state.rows[i].xs[j];
            
            int neighbors, color;
            int dead_coords[16];
            int dead_valid[8];
            get_neighbors_info(sim, x, y, &neighbors, &color, dead_coords, dead_valid);
            
            for(int k=0; k<8; k++) {
                if(dead_valid[k]) {
                    if (!is_dead_wait(sim, dead_coords[k*2], dead_coords[k*2+1])) {
                        hashmap_incr(&all_dead_neighbors, dead_coords[k*2], dead_coords[k*2+1]);
                    }
                }
            }
            
            bool survive = false;
            for(int k=0; k<sim->base.rule_s_len; k++) {
                if(neighbors == sim->base.rule_s[k]) {
                    survive = true;
                    break;
                }
            }
            
            if (survive) {
                state_add_cell(&new_state, x, y);
                hashmap_add(new_colors[color-1], x, y);
            } else {
                state_add_cell(new_dw0_n, x, y);
                hashmap_add(new_dw0_colors[color-1], x, y);
            }
        }
    }
    
    for(int i=0; i<all_dead_neighbors.size; i++) {
        Node *n = all_dead_neighbors.buckets[i];
        while(n) {
            bool birth = false;
            for(int k=0; k<sim->base.rule_b_len; k++) {
                if (n->value == sim->base.rule_b[k]) {
                    birth = true;
                    break;
                }
            }
            if (birth) {
                int x = (int)(n->key & 0xFFFFFFFF);
                int y = (int)(n->key >> 32);
                int nx = x, ny = y;
                if(sim->base.periodic) {
                    nx = periodic_x(sim, x);
                    ny = periodic_y(sim, y);
                }
                
                state_add_cell(&new_state, nx, ny);
                int color = get_color_from_alive_for_birth(sim, x, y);
                hashmap_add(new_colors[color-1], nx, ny);
            }
            n = n->next;
        }
    }
    
    State *old_last_n = sim->dead_wait_n[dw_levels - 1];
    HashMap **old_last_colors = sim->dead_wait_colors_n[dw_levels - 1];
    
    state_free(old_last_n);
    free(old_last_n);
    for(int i=0; i<3; i++) {
        hashmap_free(old_last_colors[i]);
        free(old_last_colors[i]);
    }
    free(old_last_colors);
    
    for(int c=dw_levels-1; c>0; c--) {
        sim->dead_wait_n[c] = sim->dead_wait_n[c-1];
        sim->dead_wait_colors_n[c] = sim->dead_wait_colors_n[c-1];
    }
    sim->dead_wait_n[0] = new_dw0_n;
    sim->dead_wait_colors_n[0] = new_dw0_colors;
    
    state_free(&sim->actual_state);
    for(int i=0; i<3; i++) {
        hashmap_free(sim->actual_state_colors[i]);
        free(sim->actual_state_colors[i]);
    }
    hashmap_free(&all_dead_neighbors);
    
    sim->actual_state = new_state;
    for(int i=0; i<3; i++) sim->actual_state_colors[i] = new_colors[i];
    
    JsonValue *stats = star_get_stats(sim);
    update_moving_avg(sim);
    return stats;
}

JsonValue* star_get_stats(StarSim *sim) {
    sim->livecells = state_count(&sim->actual_state);
    
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
    ADD_INT("liveCells1", sim->actual_state_colors[0]->count);
    ADD_INT("liveCells2", sim->actual_state_colors[1]->count);
    
    JsonValue *colors = calloc(1, sizeof(JsonValue));
    colors->type = JSON_ARRAY;
    colors->data.array.values = malloc(3 * sizeof(JsonValue*));
    colors->data.array.count = 3;
    for(int i=0; i<3; i++) {
        colors->data.array.values[i] = calloc(1, sizeof(JsonValue));
        colors->data.array.values[i]->type = JSON_NUMBER;
        colors->data.array.values[i]->data.number = sim->actual_state_colors[i]->count;
    }
    obj->data.object.keys[c] = my_strdup("liveCellsColors");
    obj->data.object.values[c] = colors;
    c++;
    
    double total_area = sim->base.rows * sim->base.columns;
    sim->coverage = (sim->livecells * 100.0) / (total_area + SMOL);
    ADD_DOUBLE("coverage", sim->coverage);
    
    obj->data.object.count = c;
    return obj;
}

void star_free(StarSim *sim) {
    state_free(&sim->actual_state);
    for(int i=0; i<3; i++) {
        hashmap_free(sim->actual_state_colors[i]);
        free(sim->actual_state_colors[i]);
    }
    
    for(int i=0; i<sim->rule_c - 2; i++) {
        state_free(sim->dead_wait_n[i]);
        free(sim->dead_wait_n[i]);
        for(int j=0; j<3; j++) {
            hashmap_free(sim->dead_wait_colors_n[i][j]);
            free(sim->dead_wait_colors_n[i][j]);
        }
        free(sim->dead_wait_colors_n[i]);
    }
    free(sim->dead_wait_n);
    free(sim->dead_wait_colors_n);
    
    free(sim->base.rule_b);
    free(sim->base.rule_s);
    free(sim->running_avg_window);
    free(sim);
}
