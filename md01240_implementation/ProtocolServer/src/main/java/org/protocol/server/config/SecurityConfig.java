package org.protocol.server.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.web.csrf.CsrfFilter;
import org.springframework.web.filter.CharacterEncodingFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

	@Override
	protected void configure(HttpSecurity http) throws Exception {
		CharacterEncodingFilter filter = new CharacterEncodingFilter();
		filter.setEncoding("UTF-8");
		filter.setForceEncoding(true);
		http.addFilterBefore(filter, CsrfFilter.class);
		http.csrf().disable();

		http.httpBasic().and().authorizeRequests().antMatchers("/click").hasRole("USER");

		http.authorizeRequests().antMatchers("/**").hasRole("USER");
	}

	/**
	 * Hardcoded users.
	 * 
	 * @param auth
	 * @throws Exception
	 */
	@Autowired
	public void configureGlobal(AuthenticationManagerBuilder auth) throws Exception {
		auth.inMemoryAuthentication().withUser("markos").password("doufos").roles("USER");
		auth.inMemoryAuthentication().withUser("spyros").password("kalodikis").roles("USER");
		auth.inMemoryAuthentication().withUser("james_t").password("titman").roles("USER");
		auth.inMemoryAuthentication().withUser("james_g").password("garden").roles("USER");
	}

}