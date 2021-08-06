# MetaLogo Python Package

MetaLogo provides stand alone package for user to draw figures in their own computer or server. There are two ways to make sequence logos using MetaLogo package. One is importing MetaLogo into your python scripts and create logos with specific parameters, the other is directly execute MetaLogo in system terminal and pass arguments into MetaLogo to custom the logos. These two ways share the same set of parameters, which we will explain in this tutorial.

When you installed MetaLogo, you can run MetaLogo in your terminal like this:

    $metalogo --input_file examples/test.fa --output_dir . --output_name test.png

If the command run successfully, you will get a plot named test.png in your current directory. 

Below are the parameters you can pass into MetaLogo.

    usage: metalogo [-h] [--type {Horizontal,Circle,Radiation,Threed}]
                    --input_file INPUT_FILE [--input_file_type {fasta,fastq}]
                    [--sequence_type {dna,rna,aa}] [--task_name TASK_NAME]
                    [--min_length MIN_LENGTH] [--max_length MAX_LENGTH]
                    [--group_strategy {length,identifier}]
                    [--group_order {length,length_rev,identifier,identifier}]
                    [--color_scheme {basic_dna_color,basic_rna_color,basic_aa_color}]
                    [--height_algrithm {bits,probabilities}] [--align]
                    [--padding_align]
                    [--align_metric {dot_product,js_divergence,cosine,entropy_bhattacharyya}]
                    [--connect_threshold CONNECT_THRESHOLD]
                    [--gap_score GAP_SCORE]
                    [--logo_margin_ratio LOGO_MARGIN_RATIO]
                    [--column_margin_ratio COLUMN_MARGIN_RATIO]
                    [--char_margin_ratio CHAR_MARGIN_RATIO] [--hide_version_tag]
                    [--hide_left_axis] [--hide_right_axis] [--hide_top_axis]
                    [--hide_bottom_axis] [--hide_x_ticks] [--hide_y_ticks]
                    [--hide_z_ticks] [--x_label X_LABEL] [--y_label Y_LABEL]
                    [--z_label Z_LABEL] [--show_group_id] [--show_grid]
                    [--title_size TITLE_SIZE] [--label_size LABEL_SIZE]
                    [--tick_size TICK_SIZE] [--group_id_size GROUP_ID_SIZE]
                    [--figure_size_x FIGURE_SIZE_X]
                    [--figure_size_y FIGURE_SIZE_Y] [--align_color ALIGN_COLOR]
                    [--align_alpha ALIGN_ALPHA] --output_dir OUTPUT_DIR
                    [--output_name OUTPUT_NAME]

    optional arguments:
      -h, --help            show this help message and exit
      --type {Horizontal,Circle,Radiation,Threed}
                            Choose the layout type of sequence logo (default:
                            Horizontal)
      --input_file INPUT_FILE
                            The input file contain sequences (default: None)
      --input_file_type {fasta,fastq}
                            The type of input file (default: fasta)
      --sequence_type {dna,rna,aa}
                            The type of sequences (default: dna)
      --task_name TASK_NAME
                            The title to displayed on the figure (default:
                            MetaLogo)
      --min_length MIN_LENGTH
                            The minimum length of sequences to be included
                            (default: 8)
      --max_length MAX_LENGTH
                            The maximum length of sequences to be included
                            (default: 20)
      --group_strategy {length,identifier}
                            The strategy to seperate sequences into groups
                            (default: length)
      --group_order {length,length_rev,identifier,identifier}
                            The order of groups (default: length)
      --color_scheme {basic_dna_color,basic_rna_color,basic_aa_color}
                            The color scheme (default: basic_dna_color)
      --height_algrithm {bits,probabilities}
                            The algrithm for character height (default: bits)
      --align               If show alignment of adjacent sequence logo (default:
                            False)
      --padding_align       If padding logos to make multiple logo alignment
                            (default: False)
      --align_metric {dot_product,js_divergence,cosine,entropy_bhattacharyya}
                            The metric for align score (default: dot_product)
      --connect_threshold CONNECT_THRESHOLD
                            The align threshold (default: 0.8)
      --gap_score GAP_SCORE
                            The gap score for alignment (default: -1.0)
      --logo_margin_ratio LOGO_MARGIN_RATIO
                            Margin ratio between the logos (default: 0.1)
      --column_margin_ratio COLUMN_MARGIN_RATIO
                            Margin ratio between the columns (default: 0.05)
      --char_margin_ratio CHAR_MARGIN_RATIO
                            Margin ratio between the chars (default: 0.05)
      --hide_version_tag    If show version tag of MetaLogo (default: False)
      --hide_left_axis      If hide left axis (default: False)
      --hide_right_axis     If hide right axis (default: False)
      --hide_top_axis       If hide top axis (default: False)
      --hide_bottom_axis    If hide bottom axis (default: False)
      --hide_x_ticks        If hide ticks of X axis (default: False)
      --hide_y_ticks        If hide ticks of Y axis (default: False)
      --hide_z_ticks        If hide ticks of Z axis (default: False)
      --x_label X_LABEL     The label for X axis (default: None)
      --y_label Y_LABEL     The label for Y axis (default: None)
      --z_label Z_LABEL     The label for Z axis (default: None)
      --show_group_id       If show group ids (default: False)
      --show_grid           If show background grid (default: False)
      --title_size TITLE_SIZE
                            The size of figure title (default: 20)
      --label_size LABEL_SIZE
                            The size of figure xy labels (default: 10)
      --tick_size TICK_SIZE
                            The size of figure ticks (default: 10)
      --group_id_size GROUP_ID_SIZE
                            The size of group labels (default: 10)
      --figure_size_x FIGURE_SIZE_X
                            The width of figure (default: 10)
      --figure_size_y FIGURE_SIZE_Y
                            The height of figure (default: 10)
      --align_color ALIGN_COLOR
                            The color of alignment (default: 10)
      --align_alpha ALIGN_ALPHA
                            The transparency of alignment (default: 10)
      --output_dir OUTPUT_DIR
                            Output path of figure (default: .)
      --output_name OUTPUT_NAME
                            Output name of figure (default: test.png)

Most of the parameters are easy to understand, there are several parameters need to be explained here.

      --group_strategy {length,identifier}
                            The strategy to seperate sequences into groups
                            (default: length)

This parameter specifiy the way you group sequences. In default, MetaLogo groups sequences by lengths. However, you could still 