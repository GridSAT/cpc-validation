from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(
    __file__
).resolve().parents[1]

RTL = (
    ROOT
    / "rtl"
    / "n0_controller.v"
)


def require_iverilog() -> None:
    if shutil.which(
        "iverilog"
    ) is None:
        raise RuntimeError(
            "iverilog is required"
        )

    if shutil.which(
        "vvp"
    ) is None:
        raise RuntimeError(
            "vvp is required"
        )


def run_tb(
    tmp_path: Path,
    source: str,
) -> str:
    require_iverilog()

    tb = (
        tmp_path
        / "tb.v"
    )

    executable = (
        tmp_path
        / "sim.out"
    )

    tb.write_text(
        source,
        encoding="utf-8",
    )

    compile_result = subprocess.run(
        (
            "iverilog",
            "-g2012",
            "-Wall",
            "-s",
            "tb",
            "-o",
            str(
                executable
            ),
            str(
                RTL
            ),
            str(
                tb
            ),
        ),
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        compile_result.returncode
        == 0
    )

    execution = subprocess.run(
        (
            "vvp",
            str(
                executable
            ),
        ),
        check=True,
        capture_output=True,
        text=True,
    )

    return execution.stdout


COMMON = r'''
`timescale 1ns/1ps

module tb;

    reg clk = 0;
    reg reset_n = 0;

    reg arm_i = 0;
    reg start_i = 0;
    reg device_ready_i = 0;
    reg sample_done_i = 0;
    reg fault_i = 0;

    wire probe_enable_o;
    wire acquire_enable_o;
    wire busy_o;
    wire done_o;
    wire error_o;
    wire [3:0] event_code_o;

    always #5 clk = ~clk;

    cpc_shor_n0_controller #(
        .PROBE_CYCLES(3),
        .ACQUIRE_TIMEOUT_CYCLES(5),
        .COUNTER_WIDTH(8)
    ) dut (
        .clk(clk),
        .reset_n(reset_n),
        .arm_i(arm_i),
        .start_i(start_i),
        .device_ready_i(device_ready_i),
        .sample_done_i(sample_done_i),
        .fault_i(fault_i),
        .probe_enable_o(probe_enable_o),
        .acquire_enable_o(acquire_enable_o),
        .busy_o(busy_o),
        .done_o(done_o),
        .error_o(error_o),
        .event_code_o(event_code_o)
    );

    task expect_event;
        input [3:0] expected;
        begin
            #1;
            if (event_code_o !== expected) begin
                $display(
                    "EVENT_MISMATCH expected=%h actual=%h",
                    expected,
                    event_code_o
                );
                $fatal(1);
            end
        end
    endtask
'''


def test_nominal_controller_sequence(
    tmp_path: Path,
) -> None:
    source = (
        COMMON
        + r'''
    initial begin
        #2;
        reset_n = 0;

        #10;
        reset_n = 1;
        expect_event(4'h0);

        arm_i = 1;
        @(posedge clk);
        #1;
        arm_i = 0;
        expect_event(4'h1);

        device_ready_i = 1;
        start_i = 1;
        @(posedge clk);
        #1;
        start_i = 0;
        expect_event(4'h2);

        repeat (2) begin
            @(posedge clk);
            #1;
            expect_event(4'h2);
        end

        @(posedge clk);
        #1;
        expect_event(4'h3);

        if (!acquire_enable_o) begin
            $fatal(1);
        end

        sample_done_i = 1;
        @(posedge clk);
        #1;
        sample_done_i = 0;

        expect_event(4'h4);

        if (!done_o || error_o) begin
            $fatal(1);
        end

        @(posedge clk);
        #1;
        expect_event(4'h4);

        $display("NOMINAL_PASS");
        $finish;
    end

endmodule
'''
    )

    output = run_tb(
        tmp_path,
        source,
    )

    assert (
        "NOMINAL_PASS"
        in output
    )


def test_start_without_arm_fails_closed(
    tmp_path: Path,
) -> None:
    source = (
        COMMON
        + r'''
    initial begin
        #2;
        reset_n = 0;

        #10;
        reset_n = 1;
        expect_event(4'h0);

        start_i = 1;
        device_ready_i = 1;

        @(posedge clk);
        #1;

        start_i = 0;

        expect_event(4'hF);

        if (!error_o || done_o) begin
            $fatal(1);
        end

        @(posedge clk);
        #1;
        expect_event(4'hF);

        $display("ILLEGAL_START_PASS");
        $finish;
    end

endmodule
'''
    )

    output = run_tb(
        tmp_path,
        source,
    )

    assert (
        "ILLEGAL_START_PASS"
        in output
    )


def test_acquisition_timeout_fails_closed(
    tmp_path: Path,
) -> None:
    source = (
        COMMON
        + r'''
    initial begin
        #2;
        reset_n = 0;

        #10;
        reset_n = 1;

        arm_i = 1;
        @(posedge clk);
        #1;
        arm_i = 0;

        device_ready_i = 1;
        start_i = 1;
        @(posedge clk);
        #1;
        start_i = 0;

        repeat (3) begin
            @(posedge clk);
            #1;
        end

        expect_event(4'h3);

        repeat (5) begin
            @(posedge clk);
            #1;
        end

        expect_event(4'hF);

        if (!error_o || done_o) begin
            $fatal(1);
        end

        $display("TIMEOUT_PASS");
        $finish;
    end

endmodule
'''
    )

    output = run_tb(
        tmp_path,
        source,
    )

    assert (
        "TIMEOUT_PASS"
        in output
    )


def test_fault_from_probe_fails_closed(
    tmp_path: Path,
) -> None:
    source = (
        COMMON
        + r'''
    initial begin
        #2;
        reset_n = 0;

        #10;
        reset_n = 1;

        arm_i = 1;
        @(posedge clk);
        #1;
        arm_i = 0;

        device_ready_i = 1;
        start_i = 1;
        @(posedge clk);
        #1;
        start_i = 0;

        expect_event(4'h2);

        fault_i = 1;
        @(posedge clk);
        #1;
        fault_i = 0;

        expect_event(4'hF);

        if (!error_o) begin
            $fatal(1);
        end

        $display("FAULT_PASS");
        $finish;
    end

endmodule
'''
    )

    output = run_tb(
        tmp_path,
        source,
    )

    assert (
        "FAULT_PASS"
        in output
    )


def test_reset_recovers_terminal_error(
    tmp_path: Path,
) -> None:
    source = (
        COMMON
        + r'''
    initial begin
        #2;
        reset_n = 0;

        #10;
        reset_n = 1;

        start_i = 1;
        @(posedge clk);
        #1;
        start_i = 0;

        expect_event(4'hF);

        reset_n = 0;
        #1;
        expect_event(4'h0);

        reset_n = 1;
        #1;
        expect_event(4'h0);

        if (
            done_o
            || error_o
            || busy_o
            || probe_enable_o
            || acquire_enable_o
        ) begin
            $fatal(1);
        end

        $display("RESET_RECOVERY_PASS");
        $finish;
    end

endmodule
'''
    )

    output = run_tb(
        tmp_path,
        source,
    )

    assert (
        "RESET_RECOVERY_PASS"
        in output
    )
