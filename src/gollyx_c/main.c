#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "golly.h"

static char* read_file(const char* filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = 0;
    fclose(f);
    return buf;
}

#include <time.h>

#define MAX_TOTAL_STEPS 20000

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input.json>\n", argv[0]);
        return 1;
    }
    
    char *json_str = read_file(argv[1]);
    if (!json_str) {
        fprintf(stderr, "Error reading file %s\n", argv[1]);
        return 1;
    }
    
    JsonValue *root = json_parse(json_str);
    if (!root) {
        fprintf(stderr, "Error parsing JSON\n");
        free(json_str);
        return 1;
    }
    
    // Detect Sim Type
    bool is_star = false;
    if (json_get(root, "initialConditionsb1")) is_star = true;
    if (!is_star && json_get(root, "initialConditionsc1")) is_star = true;
    
    time_t start_time = time(NULL);
    int timeout_seconds = 240; // 4 minutes

    if (is_star) {
        StarSim *sim = star_new(root);
        JsonValue *res = NULL;
        int max_gens = MAX_TOTAL_STEPS;
        int gen = 0;
        while (sim->base.running && gen < max_gens) {
            if (res) json_free(res);
            res = star_step(sim);
            gen++;
            if (gen % 100 == 0) {
                if (difftime(time(NULL), start_time) > timeout_seconds) {
                    fprintf(stderr, "Timeout reached (%d seconds). Stopping.\n", timeout_seconds);
                    break;
                }
            }
        }
        
        printf("{\n");
        printf("  \"generation\": %d,\n", (int)json_as_number(json_get(res, "generation")));
        printf("  \"liveCells\": %d,\n", (int)json_as_number(json_get(res, "liveCells")));
        printf("  \"liveCells1\": %d,\n", (int)json_as_number(json_get(res, "liveCells1")));
        printf("  \"liveCells2\": %d,\n", (int)json_as_number(json_get(res, "liveCells2")));
        printf("  \"coverage\": %.6f,\n", json_as_number(json_get(res, "coverage")));
        printf("  \"found_victor\": %s,\n", sim->base.found_victor ? "true" : "false");
        printf("  \"who_won\": %d\n", sim->base.who_won);
        printf("}\n");
        
        json_free(res);
        star_free(sim);
    } else {
        ToroidalSim *sim = toroidal_new(root);
        JsonValue *res = NULL;
        int max_gens = MAX_TOTAL_STEPS;
        int gen = 0;
        while (sim->base.running && gen < max_gens) {
            if (res) json_free(res);
            res = toroidal_step(sim);
            gen++;
            if (gen % 1000 == 0) {
                if (difftime(time(NULL), start_time) > timeout_seconds) {
                    fprintf(stderr, "Timeout reached (%d seconds). Stopping.\n", timeout_seconds);
                    break;
                }
            }
        }
        
        printf("{\n");
        printf("  \"generation\": %d,\n", (int)json_as_number(json_get(res, "generation")));
        printf("  \"liveCells\": %d,\n", (int)json_as_number(json_get(res, "liveCells")));
        printf("  \"liveCells1\": %d,\n", (int)json_as_number(json_get(res, "liveCells1")));
        printf("  \"liveCells2\": %d,\n", (int)json_as_number(json_get(res, "liveCells2")));
        printf("  \"victoryPct\": %.6f,\n", json_as_number(json_get(res, "victoryPct")));
        printf("  \"coverage\": %.6f,\n", json_as_number(json_get(res, "coverage")));
        printf("  \"found_victor\": %s,\n", sim->base.found_victor ? "true" : "false");
        printf("  \"who_won\": %d\n", sim->base.who_won);
        printf("}\n");
        
        json_free(res);
        toroidal_free(sim);
    }
    
    json_free(root);
    free(json_str);
    return 0;
}
