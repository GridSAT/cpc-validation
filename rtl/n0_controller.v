`default_nettype none

module cpc_shor_n0_controller #(
    parameter integer PROBE_CYCLES = 4,
    parameter integer ACQUIRE_TIMEOUT_CYCLES = 16,
    parameter integer COUNTER_WIDTH = 16
) (
    input  wire       clk,
    input  wire       reset_n,

    input  wire       arm_i,
    input  wire       start_i,
    input  wire       device_ready_i,
    input  wire       sample_done_i,
    input  wire       fault_i,

    output reg        probe_enable_o,
    output reg        acquire_enable_o,
    output reg        busy_o,
    output reg        done_o,
    output reg        error_o,
    output reg [3:0]  event_code_o
);

    localparam [2:0] STATE_IDLE    = 3'd0;
    localparam [2:0] STATE_ARMED   = 3'd1;
    localparam [2:0] STATE_PROBE   = 3'd2;
    localparam [2:0] STATE_ACQUIRE = 3'd3;
    localparam [2:0] STATE_DONE    = 3'd4;
    localparam [2:0] STATE_ERROR   = 3'd5;

    localparam [3:0] EVENT_IDLE    = 4'h0;
    localparam [3:0] EVENT_ARMED   = 4'h1;
    localparam [3:0] EVENT_PROBE   = 4'h2;
    localparam [3:0] EVENT_ACQUIRE = 4'h3;
    localparam [3:0] EVENT_DONE    = 4'h4;
    localparam [3:0] EVENT_ERROR   = 4'hF;

    reg [2:0] state;
    reg [COUNTER_WIDTH-1:0] counter;

    initial begin
        if (PROBE_CYCLES < 1) begin
            $error("PROBE_CYCLES must be >= 1");
        end

        if (ACQUIRE_TIMEOUT_CYCLES < 1) begin
            $error(
                "ACQUIRE_TIMEOUT_CYCLES must be >= 1"
            );
        end

        if (COUNTER_WIDTH < 1) begin
            $error("COUNTER_WIDTH must be >= 1");
        end
    end

    always @(*) begin
        probe_enable_o   = 1'b0;
        acquire_enable_o = 1'b0;
        busy_o           = 1'b0;
        done_o           = 1'b0;
        error_o          = 1'b0;
        event_code_o     = EVENT_ERROR;

        case (state)
            STATE_IDLE: begin
                event_code_o = EVENT_IDLE;
            end

            STATE_ARMED: begin
                event_code_o = EVENT_ARMED;
            end

            STATE_PROBE: begin
                probe_enable_o = 1'b1;
                busy_o         = 1'b1;
                event_code_o   = EVENT_PROBE;
            end

            STATE_ACQUIRE: begin
                acquire_enable_o = 1'b1;
                busy_o           = 1'b1;
                event_code_o     = EVENT_ACQUIRE;
            end

            STATE_DONE: begin
                done_o       = 1'b1;
                event_code_o = EVENT_DONE;
            end

            STATE_ERROR: begin
                error_o      = 1'b1;
                event_code_o = EVENT_ERROR;
            end

            default: begin
                error_o      = 1'b1;
                event_code_o = EVENT_ERROR;
            end
        endcase
    end

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state   <= STATE_IDLE;
            counter <= {COUNTER_WIDTH{1'b0}};
        end else begin
            case (state)
                STATE_IDLE: begin
                    counter <= {COUNTER_WIDTH{1'b0}};

                    if (fault_i) begin
                        state <= STATE_ERROR;
                    end else if (start_i) begin
                        state <= STATE_ERROR;
                    end else if (arm_i) begin
                        state <= STATE_ARMED;
                    end
                end

                STATE_ARMED: begin
                    counter <= {COUNTER_WIDTH{1'b0}};

                    if (fault_i) begin
                        state <= STATE_ERROR;
                    end else if (start_i) begin
                        if (device_ready_i) begin
                            state <= STATE_PROBE;
                        end else begin
                            state <= STATE_ERROR;
                        end
                    end
                end

                STATE_PROBE: begin
                    if (fault_i) begin
                        state   <= STATE_ERROR;
                        counter <= {
                            COUNTER_WIDTH{1'b0}
                        };
                    end else if (
                        counter
                        == PROBE_CYCLES - 1
                    ) begin
                        state   <= STATE_ACQUIRE;
                        counter <= {
                            COUNTER_WIDTH{1'b0}
                        };
                    end else begin
                        counter <= counter + 1'b1;
                    end
                end

                STATE_ACQUIRE: begin
                    if (fault_i) begin
                        state   <= STATE_ERROR;
                        counter <= {
                            COUNTER_WIDTH{1'b0}
                        };
                    end else if (sample_done_i) begin
                        state   <= STATE_DONE;
                        counter <= {
                            COUNTER_WIDTH{1'b0}
                        };
                    end else if (
                        counter
                        == ACQUIRE_TIMEOUT_CYCLES - 1
                    ) begin
                        state   <= STATE_ERROR;
                        counter <= {
                            COUNTER_WIDTH{1'b0}
                        };
                    end else begin
                        counter <= counter + 1'b1;
                    end
                end

                STATE_DONE: begin
                    state <= STATE_DONE;
                end

                STATE_ERROR: begin
                    state <= STATE_ERROR;
                end

                default: begin
                    state   <= STATE_ERROR;
                    counter <= {
                        COUNTER_WIDTH{1'b0}
                    };
                end
            endcase
        end
    end

endmodule

`default_nettype wire
