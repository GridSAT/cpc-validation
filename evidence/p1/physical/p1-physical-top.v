// CPC FPGA backend prepared execution
// backend: fpga/1
// target: Verilog-2001
//
// Internal completions are instantiated structurally.
// No expected continuation value is embedded.

module cpc_fpga_execution(
    output wire result
);

  wire x0;
  assign x0 = 1'b0;
  wire x3;
  assign x3 = 1'b1;

  // Internal completion 0
  wire completion_0_x1;
  assign completion_0_x1 = 1'b0;
  wire completion_0_x2;
  assign completion_0_x2 = 1'b0;
  wire completion_0_parity_0;
  assign completion_0_parity_0 = x0 ^ completion_0_x1 ^ completion_0_x2;
  wire completion_0_match_0;
  assign completion_0_match_0 = (completion_0_parity_0 == 1'b0);
  wire completion_0_parity_1;
  assign completion_0_parity_1 = completion_0_x1 ^ completion_0_x2 ^ x3;
  wire completion_0_match_1;
  assign completion_0_match_1 = (completion_0_parity_1 == 1'b1);
  wire completion_0;
  assign completion_0 = completion_0_match_0 & completion_0_match_1;

  // Internal completion 1
  wire completion_1_x1;
  assign completion_1_x1 = 1'b0;
  wire completion_1_x2;
  assign completion_1_x2 = 1'b1;
  wire completion_1_parity_0;
  assign completion_1_parity_0 = x0 ^ completion_1_x1 ^ completion_1_x2;
  wire completion_1_match_0;
  assign completion_1_match_0 = (completion_1_parity_0 == 1'b0);
  wire completion_1_parity_1;
  assign completion_1_parity_1 = completion_1_x1 ^ completion_1_x2 ^ x3;
  wire completion_1_match_1;
  assign completion_1_match_1 = (completion_1_parity_1 == 1'b1);
  wire completion_1;
  assign completion_1 = completion_1_match_0 & completion_1_match_1;

  // Internal completion 2
  wire completion_2_x1;
  assign completion_2_x1 = 1'b1;
  wire completion_2_x2;
  assign completion_2_x2 = 1'b0;
  wire completion_2_parity_0;
  assign completion_2_parity_0 = x0 ^ completion_2_x1 ^ completion_2_x2;
  wire completion_2_match_0;
  assign completion_2_match_0 = (completion_2_parity_0 == 1'b0);
  wire completion_2_parity_1;
  assign completion_2_parity_1 = completion_2_x1 ^ completion_2_x2 ^ x3;
  wire completion_2_match_1;
  assign completion_2_match_1 = (completion_2_parity_1 == 1'b1);
  wire completion_2;
  assign completion_2 = completion_2_match_0 & completion_2_match_1;

  // Internal completion 3
  wire completion_3_x1;
  assign completion_3_x1 = 1'b1;
  wire completion_3_x2;
  assign completion_3_x2 = 1'b1;
  wire completion_3_parity_0;
  assign completion_3_parity_0 = x0 ^ completion_3_x1 ^ completion_3_x2;
  wire completion_3_match_0;
  assign completion_3_match_0 = (completion_3_parity_0 == 1'b0);
  wire completion_3_parity_1;
  assign completion_3_parity_1 = completion_3_x1 ^ completion_3_x2 ^ x3;
  wire completion_3_match_1;
  assign completion_3_match_1 = (completion_3_parity_1 == 1'b1);
  wire completion_3;
  assign completion_3 = completion_3_match_0 & completion_3_match_1;

  assign result = completion_0 | completion_1 | completion_2 | completion_3;


endmodule

module cpc_physical_top(
    output wire result_out
);

  wire result;

  cpc_fpga_execution execution (
      .result(result)
  );

  assign result_out = result;

endmodule
