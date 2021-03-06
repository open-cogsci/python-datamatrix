title: DataMatrix

`DataMatrix` is an intuitive Python library for working with column-based and continuous data.

<div class="btn-group" role="group" aria-label="...">
  <a role="button" class="btn btn-success" href="%url:install%">
		<span class="glyphicon glyphicon-download" aria-hidden="true"></span>
		Install
	 </a>
  <a role="button" class="btn btn-success" href="%url:basic%">
  <span class="glyphicon glyphicon-education" aria-hidden="true"></span>
  	Basic use
  </a>
  <a role="button" class="btn btn-success" href="http://forum.cogsci.nl/">
  <span class="glyphicon glyphicon-comment" aria-hidden="true"></span>
  Forum</a>
</div>


## Features

- [An intuitive syntax](%link:basic%) that makes your code easy to read
- Requires only the Python standard libraries (but you can use `numpy` to improve performance)
- Great support for [functional programming](%link:functional%), including advanced [memoization (caching)](%link:memoization%)
- Mix [two-dimensional](%link:series%) (series) and one-dimensional data in a single data structure
- Compatible with your favorite tools for numeric computation:
    - `seaborn` for [plotting](%link:plotting%)
    - `statsmodels` for [statistics](%link:statistics%)
    - [Convert](%link:convert%) to and from `pandas.DataFrame`
    - Looks pretty inside a Jupyter Notebook


## Example

%--
python: |
 from datamatrix import DataMatrix
 # Four philosophers with their names, fields, and genders
 dm = DataMatrix(length=4)
 dm.name = 'Ibn al-Haytam', 'Hypatia', 'Popper', 'de Beauvoir'
 dm.field = 'Optics', 'Mathematics', 'Science', 'Existentialism'
 dm.gender = 'M', 'F', 'M', 'F'
 print('Philosophers:')
 print(dm)
 # Select only women existentialists
 dm = (dm.gender == 'F') & (dm.field == 'Existentialism')
 print('Women Existentialists:')
 print(dm)
--%
