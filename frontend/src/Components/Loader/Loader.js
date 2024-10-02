import React from 'react'
import './Loader.css'

export default function Loader() {
	return (
		<React.Fragment>
			<div className="loader-wrapper">
				<div className="lds-spinner">
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
					<div />
				</div>
				<div className="lds-comment"></div>
			</div>
		</React.Fragment>
	)
}
