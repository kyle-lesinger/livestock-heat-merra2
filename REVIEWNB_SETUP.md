# ReviewNB Setup for Jupyter Notebook Reviews

This repository uses [ReviewNB](https://www.reviewnb.com/) to provide visual diffs and commenting for Jupyter notebooks in pull requests.

## Why ReviewNB?

Traditional git diffs for `.ipynb` files are difficult to read because notebooks are stored as JSON. ReviewNB provides:

- **Visual Diffs**: See cell-by-cell changes with rendered outputs
- **Cell-Level Comments**: Comment on specific notebook cells during code review
- **Output Comparison**: Compare plot outputs, tables, and other cell outputs visually
- **GitHub Integration**: Works seamlessly with GitHub pull requests

## Installation

### For Repository Owners

1. Visit [ReviewNB GitHub App](https://github.com/apps/review-notebook-app)
2. Click "Install" or "Configure"
3. Select the `livestock-heat-merra2` repository
4. Grant the necessary permissions (read access to pull requests and notebooks)
5. That's it! ReviewNB will automatically appear on pull requests containing notebook changes

### For Contributors

No installation needed! Once ReviewNB is installed on the repository:

1. Create a pull request with notebook changes as usual
2. ReviewNB will automatically comment on the PR with a link to the visual diff
3. Click the ReviewNB link to see rendered notebook changes
4. Add comments directly on notebook cells

## Using ReviewNB

### Viewing Notebook Diffs

1. When you open a pull request with notebook changes, look for the ReviewNB bot comment
2. Click the "View on ReviewNB" link
3. You'll see a side-by-side comparison of notebook changes with:
   - Code cells with syntax highlighting
   - Rendered markdown cells
   - Output cells (plots, tables, text output)
   - Added/removed/modified cells clearly marked

### Commenting on Notebooks

1. In the ReviewNB interface, hover over any cell
2. Click the comment icon that appears
3. Write your review comment (supports markdown)
4. Comments sync back to the GitHub PR conversation

### Best Practices

**Before Creating a PR:**

1. **Clear unnecessary outputs** from experimental/debug cells:
   ```python
   # In Jupyter: Cell > All Output > Clear
   # Or use jupyter nbconvert --clear-output
   ```

2. **Run notebooks from top to bottom** to ensure reproducibility:
   ```python
   # Kernel > Restart & Run All
   ```

3. **Keep output sizes reasonable**:
   - Limit large dataframe displays (use `.head()`)
   - Reduce plot DPI if not needed for review
   - Consider clearing outputs from large datasets

**During Review:**

1. **Check cell execution order**: Ensure cells are numbered sequentially (1, 2, 3...)
2. **Verify outputs match code**: Make sure plots/tables reflect the code changes
3. **Review markdown documentation**: Check that explanations are clear and accurate
4. **Test reproducibility**: Can the notebook be run top-to-bottom without errors?

## Notebook Organization

Our notebooks are organized into directories:

- `notebooks/01_data_ingestion/` - MERRA-2 data download and initial processing
- `notebooks/02_data_processing/` - Statistical calculations and metric derivation
- `notebooks/03_analysis/` - Temporal, spatial, and multivariate analysis
- `notebooks/04_visualization/` - Final plots and figures

When reviewing notebooks, consider which category they belong to and whether they follow the conventions established in that directory.

## Common Review Checklist

- [ ] Notebook runs from top to bottom without errors
- [ ] Cell execution order is sequential (1, 2, 3, ...)
- [ ] Imports are at the top of the notebook
- [ ] Code follows project style guidelines (see `.clinerules.md`)
- [ ] Markdown cells provide clear explanations
- [ ] Plots use standardized configuration (`plot_config.py`)
- [ ] Output files are saved to appropriate directories
- [ ] Large data files are not committed (check `.gitignore`)
- [ ] Sensitive data or credentials are not exposed

## Troubleshooting

**ReviewNB bot doesn't comment on my PR:**
- Ensure the PR contains actual notebook (`.ipynb`) changes
- Check that ReviewNB is installed on the repository
- Try closing and reopening the PR

**Can't see notebook outputs in ReviewNB:**
- Outputs may be stripped if notebooks were cleaned before commit
- This is expected for some workflows - review the code logic instead

**ReviewNB shows large diffs for minor changes:**
- Notebooks store metadata (execution counts, timestamps) that can cause noise
- Focus on actual code and output changes
- Consider using `nbstripout` to remove metadata (see below)

## Advanced: nbstripout (Optional)

To automatically strip metadata and outputs before committing:

```bash
# Install nbstripout
pip install nbstripout

# Set up git filter for this repository
nbstripout --install

# This will strip metadata from notebooks before they're staged
```

Note: Discuss with the team before implementing this, as it removes all outputs.

## Resources

- [ReviewNB Documentation](https://www.reviewnb.com/docs)
- [ReviewNB GitHub App](https://github.com/apps/review-notebook-app)
- [Jupyter Notebook Best Practices](https://www.reviewnb.com/jupyter-notebook-best-practices)

## Questions?

For issues with ReviewNB setup or usage, contact the repository maintainer or open an issue on GitHub.
